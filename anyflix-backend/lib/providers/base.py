"""Base provider class similar to JavaScript MProvider."""

import contextlib
import re
from abc import ABC, abstractmethod
from typing import Any

import httpx

from lib.extractors.extract_any import extract_any
from lib.models.base import (
    MediaInfo,
    MediaSource,
    SearchResult,
    SourcePreference,
)
from lib.models.responses import (
    PaginatedSearchResultResponse,
    VideoListResponse,
)
from lib.utils.caching import ServiceCacheConfig, cached
from lib.utils.client import HTTPClient
from lib.utils.helpers import async_pool, clean_html_string
from lib.utils.logging_config import get_logger
from lib.utils.parser import Document
from lib.utils.url_utils import normalize_url


def map_language_to_code(lang: str) -> str:
    """Map language names to standard language codes.

    Args:
        lang: Language name (e.g., 'Deutsch', 'Englisch') or code (e.g., 'de', 'en')

    Returns:
        Standard language code (e.g., 'de', 'en', 'sub', 'all')
    """
    if not lang:
        return "all"

    lang_lower = lang.lower()

    # Handle direct language codes
    if lang_lower in ["de", "en", "sub", "all"]:
        return lang_lower

    # Handle language names
    if "deutsch" in lang_lower:
        return "de"
    if "englisch" in lang_lower or "english" in lang_lower:
        return "en"
    return "sub"  # Default fallback


class BaseProvider(ABC):
    """Base class for media source providers (anime/series)."""

    # Maximum items per page for pagination (can be overridden)
    ITEMS_PER_PAGE = 15

    # URL patterns for film/movie detection (can be overridden)
    FILM_URL_PATTERN = r"/filme?/film-(\d+)"

    def __init__(self, source: MediaSource) -> None:
        """Initialize provider with source configuration.

        Args:
            source: Source configuration
        """
        self.source = source
        self.client = HTTPClient()
        self.logger = get_logger(self.__class__.__module__)

        # Determine if this is an anime source
        self.is_anime_source = (
            "anime" in source.name.lower() or "aniworld" in source.name.lower()
        )
        self.response_type = "anime" if self.is_anime_source else "normal"

    async def __aenter__(self):
        """Async context manager entry."""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    # =========================================================================
    # URL & String Helpers
    # =========================================================================

    def _build_full_url(self, path: str) -> str:
        """Build full URL from base URL and path.

        Args:
            path: URL path (can start with / or not, or be absolute)

        Returns:
            Full URL
        """
        if not path:
            return ""
        base_url = self.source.base_url
        if path.startswith("http"):
            return path
        if path.startswith("/"):
            return base_url + path
        return f"{base_url}/{path}"

    def _safe_extract_text(self, element: Any, default: str = "") -> str:
        """Safely extract text from an element.

        Args:
            element: DOM element (can be None)
            default: Default value if element is None or empty

        Returns:
            Element text or default value
        """
        if element and element._element:
            return element.text or default
        return default

    def _safe_extract_attr(
        self, element: Any, attr_name: str, default: str = ""
    ) -> str:
        """Safely extract attribute from an element.

        Args:
            element: DOM element (can be None)
            attr_name: Attribute name to extract
            default: Default value if element is None or attribute doesn't exist

        Returns:
            Attribute value or default value
        """
        if element and element._element:
            return element.attr(attr_name) or default
        return default

    def _extract_list_from_elements(
        self, elements: list, exclude_pattern: str = r"^\s*&\s*\d+\s*weitere\s*$"
    ) -> list[str]:
        """Extract text list from elements, filtering out unwanted patterns.

        Args:
            elements: List of DOM elements
            exclude_pattern: Regex pattern to exclude (e.g., "& 5 weitere")

        Returns:
            List of cleaned text values
        """
        result = []
        for elem in elements:
            if elem._element:
                text = elem.text.strip()
                if text and not re.match(exclude_pattern, text):
                    result.append(text)
        return result

    def clean_html_string(self, input_str: str) -> str:
        """Clean HTML string helper.

        Args:
            input_str: Input string to clean

        Returns:
            Cleaned string
        """
        return clean_html_string(input_str)

    # =========================================================================
    # List Parsing
    # =========================================================================

    async def _parse_media_list_elements(
        self, elements: list, fetch_details: bool = True
    ) -> list[SearchResult]:
        """Parse media list elements into SearchResult objects.

        Common method for parsing series/anime list containers from both providers.

        Args:
            elements: DOM elements containing media data (div.seriesListContainer div)
            fetch_details: Whether to fetch full media_info for each result

        Returns:
            List of SearchResult objects with optional media_info
        """
        # First pass: extract basic info from elements
        basic_results = []
        for element in elements:
            link_element = element.select_first("a")
            name_element = element.select_first("h3")
            img_element = (
                link_element.select_first("img") if link_element._element else None
            )

            if (
                link_element._element
                and name_element._element
                and img_element
                and img_element._element
            ):
                name = name_element.text
                image_path = img_element.attr("data-src")
                image_url = self._build_full_url(image_path)
                link = link_element.attr("href")
                basic_results.append((name, image_url, link))

        # Second pass: fetch media_info concurrently if requested
        if fetch_details and basic_results:

            async def fetch_detail(item: tuple) -> SearchResult:
                name, image_url, link = item
                try:
                    media_info = await self.get_detail(link, episodes=False)
                    available_languages = (
                        media_info.available_languages if media_info else []
                    )
                except Exception:
                    self.logger.exception("Failed to fetch detail for %s", link)
                    media_info = None
                    available_languages = []
                return SearchResult(
                    name=name,
                    image_url=image_url,
                    link=link,
                    provider=self.source.name,
                    available_languages=available_languages,
                    media_info=media_info,
                )

            # Use async_pool with concurrency limit to avoid overwhelming the server
            return await self.async_pool(3, basic_results, fetch_detail)

        # Return results without media_info
        return [
            SearchResult(
                name=name,
                image_url=image_url,
                link=link,
                provider=self.source.name,
            )
            for name, image_url, link in basic_results
        ]

    # =========================================================================
    # Pagination
    # =========================================================================

    def _apply_pagination(self, items: list, page: int) -> tuple[list, bool]:
        """Apply pagination to a list of items.

        Args:
            items: List of items to paginate
            page: Page number (1-based)

        Returns:
            Tuple of (paginated_items, has_next_page)
        """
        items_per_page = self.ITEMS_PER_PAGE
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page

        paginated_items = items[start_index:end_index]
        has_next_page = end_index < len(items)

        return paginated_items, has_next_page

    # =========================================================================
    # Async Helpers
    # =========================================================================

    async def async_pool(
        self, pool_limit: int, array: list, iterator_fn: callable
    ) -> list:
        """Async pool helper.

        Args:
            pool_limit: Maximum concurrent operations
            array: Items to process
            iterator_fn: Function to apply to each item

        Returns:
            List of results
        """
        return await async_pool(pool_limit, array, iterator_fn)

    # =========================================================================
    # Metadata Extraction (shared HTML structure)
    # =========================================================================

    def _extract_extended_metadata(
        self, document: Document, _base_url: str
    ) -> dict[str, Any]:
        """Extract extended metadata from seriesContentBox.

        Works for both AniWorld and SerienStream as they share the same HTML structure.

        Args:
            document: Parsed HTML document
            base_url: Base URL for resolving relative URLs

        Returns:
            Dictionary with extracted metadata
        """
        metadata: dict[str, Any] = {}

        # === Required Fields ===
        # Extract name
        name_element = document.select_first("div.series-title h1 span")
        metadata["name"] = self._safe_extract_text(name_element).strip()

        # Extract description from data-full-description attribute
        desc_element = document.select_first("p.seri_des")
        full_desc = self._safe_extract_attr(desc_element, "data-full-description")
        metadata["description"] = self.clean_html_string(full_desc)

        # Extract cover image (try data-src first, fallback to src)
        cover_element = document.select_first("div.seriesCoverBox img")
        cover_path = self._safe_extract_attr(
            cover_element, "data-src"
        ) or self._safe_extract_attr(cover_element, "src")
        metadata["cover_image_url"] = (
            self._build_full_url(cover_path) if cover_path else ""
        )

        # === Alternative Titles ===
        # Try both camelCase and lowercase versions of the attribute
        title_element = document.select_first(
            "div.series-title h1[data-alternativetitles]"
        ) or document.select_first("div.series-title h1[data-alternativeTitles]")
        alt_titles_str = self._safe_extract_attr(
            title_element, "data-alternativetitles"
        ) or self._safe_extract_attr(title_element, "data-alternativeTitles")
        if alt_titles_str:
            metadata["alternative_titles"] = [
                t.strip() for t in alt_titles_str.split(",") if t.strip()
            ]

        # === Years ===
        start_year_element = document.select_first('span[itemprop="startDate"] a')
        start_year_text = self._safe_extract_text(start_year_element)
        if start_year_text:
            with contextlib.suppress(ValueError, TypeError):
                metadata["start_year"] = int(start_year_text)

        end_year_element = document.select_first('span[itemprop="endDate"] a')
        end_year_text = self._safe_extract_text(end_year_element)
        if end_year_text and end_year_text != "Heute":  # "Today" in German
            with contextlib.suppress(ValueError, TypeError):
                metadata["end_year"] = int(end_year_text)

        # === Ratings ===
        # FSK age rating
        fsk_element = document.select_first("div[data-fsk]")
        fsk_value = self._safe_extract_attr(fsk_element, "data-fsk")
        if fsk_value:
            with contextlib.suppress(ValueError, TypeError):
                metadata["fsk_rating"] = int(fsk_value)

        # === External IDs ===
        imdb_element = document.select_first("a[data-imdb]")
        imdb_id = self._safe_extract_attr(imdb_element, "data-imdb")
        if imdb_id:
            metadata["imdb_id"] = imdb_id

        # === Country ===
        country_element = document.select_first(
            'li[data-content-type="country"] span[itemprop="name"]'
        )
        country = self._safe_extract_text(country_element)
        if country:
            metadata["country_of_origin"] = country

        # === Genres ===
        # Filter out "+ X" patterns (hidden genre count indicators)
        genre_elements = document.select("div.genres ul li a")
        genres = self._extract_list_from_elements(
            genre_elements, exclude_pattern=r"^\+\s*\d+$"
        )
        if genres:
            metadata["genres"] = genres

        # Main genre from data attribute
        main_genre_element = document.select_first("div.genres ul[data-main-genre]")
        main_genre = self._safe_extract_attr(main_genre_element, "data-main-genre")
        if main_genre:
            metadata["main_genre"] = main_genre

        # === Cast & Crew ===
        # Directors
        director_elements = document.select(
            "li.seriesDirector ul li span[itemprop='name']"
        )
        directors = self._extract_list_from_elements(director_elements)
        if directors:
            metadata["directors"] = directors

        # Actors
        actor_elements = document.select(
            "li .seriesActor ~ ul li span[itemprop='name']"
        )
        actors = self._extract_list_from_elements(actor_elements)
        if actors:
            metadata["actors"] = actors

        # Producers/Studios
        producer_elements = document.select(
            "li .seriesProducer ~ ul li span[itemprop='name']"
        )
        producers = self._extract_list_from_elements(producer_elements)
        if producers:
            metadata["producers"] = producers

        # === Images ===
        # Backdrop URL from style attribute
        backdrop_element = document.select_first("div.backdrop")
        backdrop_style = self._safe_extract_attr(backdrop_element, "style")
        if backdrop_style:
            match = re.search(r"url\(([^)]+)\)", backdrop_style)
            if match:
                backdrop_path = match.group(1).strip("'\"")
                metadata["backdrop_url"] = self._build_full_url(backdrop_path)

        # === Provider IDs ===
        series_id_element = document.select_first("div.add-series[data-series-id]")
        series_id = self._safe_extract_attr(series_id_element, "data-series-id")
        if series_id:
            metadata["series_id"] = series_id

        # === Trailer URL ===
        # Try multiple selectors for trailer
        trailer_element = document.select_first(
            "a.trailerButton[itemprop='url']"
        ) or document.select_first("div[itemprop='trailer'] a[itemprop='url']")
        trailer_url = self._safe_extract_attr(trailer_element, "href")
        if trailer_url:
            metadata["trailer_url"] = trailer_url

        # === User Ratings ===
        # Extract aggregate rating from schema.org markup
        rating_value_element = document.select_first("span[itemprop='ratingValue']")
        rating_value_text = self._safe_extract_text(rating_value_element)
        if rating_value_text:
            with contextlib.suppress(ValueError, TypeError):
                metadata["rating_value"] = float(rating_value_text)

        rating_count_element = document.select_first("span[itemprop='ratingCount']")
        rating_count_text = self._safe_extract_text(rating_count_element)
        if rating_count_text:
            with contextlib.suppress(ValueError, TypeError):
                metadata["rating_count"] = int(rating_count_text)

        # === Available Languages ===
        # Extract from episode table flag images
        available_languages = self._extract_available_languages(document)
        if available_languages:
            metadata["available_languages"] = available_languages

        return metadata

    def _extract_available_languages(self, document: Document) -> list[str]:
        """Extract available languages from episode flag images.

        Parses flag images in the episode table to determine available audio/subtitle options.

        Args:
            document: Parsed HTML document

        Returns:
            List of language codes (de, en, de_sub, en_sub)
        """
        languages = set()

        # Find all flag images in the episode table
        flag_elements = document.select("td.editFunctions img.flag")

        for flag in flag_elements:
            if not flag._element:
                continue

            src = self._safe_extract_attr(flag, "src").lower()
            title = self._safe_extract_attr(flag, "title").lower()

            # Map flag images to language codes
            # Check for subtitle patterns FIRST (more specific)
            if "japanese-german" in src:
                # Japanese audio with German subtitles
                languages.add("de_sub")
            elif "japanese-english" in src:
                # Japanese audio with English subtitles
                languages.add("en_sub")
            elif "german.svg" in src or "german.png" in src:
                # German dub (standalone german flag, not japanese-german)
                languages.add("de")
            elif "english.svg" in src or "english.png" in src:
                # English dub (standalone english flag, not japanese-english)
                languages.add("en")
            elif "untertitel" in title or "sub" in title:
                # Fallback: check title for subtitle indicators
                if "deutsch" in title:
                    languages.add("de_sub")
                elif "english" in title or "englisch" in title:
                    languages.add("en_sub")

        # Sort for consistent ordering: dubs first, then subs
        order = {"de": 0, "en": 1, "de_sub": 2, "en_sub": 3}
        return sorted(languages, key=lambda x: order.get(x, 99))

    # =========================================================================
    # Detail & Episode Parsing
    # =========================================================================

    @cached(ttl=ServiceCacheConfig.PROVIDER_DETAIL_TTL, key_prefix="provider_detail")
    async def get_detail(self, url: str, episodes: bool = True) -> MediaInfo:
        """Get media details.

        Args:
            url: Media URL
            episodes: Whether to fetch episode list

        Returns:
            MediaInfo with details
        """
        # Use robust URL normalization
        full_url = normalize_url(self.source.base_url, url)

        self.logger.debug("Fetching detail from: %s", full_url)
        res = await self.client.get(full_url)
        document = Document(res.body)

        # Extract extended metadata (includes basic info)
        extended_metadata = self._extract_extended_metadata(
            document, self.source.base_url
        )

        # Extract episodes
        seasons_elements = document.select("#stream > ul:nth-child(1) > li > a")
        # Process seasons with concurrency limit
        if episodes:
            episodes_arrays = await self.async_pool(
                2, seasons_elements, self.parse_episodes_from_series
            )
        else:
            episodes_arrays = []
        seasons_length = len(seasons_elements)

        # Flatten and reverse episodes
        all_episodes = []
        for ep_array in episodes_arrays:
            all_episodes.extend(ep_array)
        all_episodes.reverse()

        # Add episodes to the metadata and create MediaInfo
        extended_metadata["episodes"] = all_episodes
        extended_metadata["seasons_length"] = seasons_length

        return MediaInfo(**extended_metadata)

    async def parse_episodes_from_series(self, element: Any) -> list[dict[str, Any]]:
        """Parse episodes from a season.

        Args:
            element: Season element

        Returns:
            List of episodes
        """
        season_id = element.get_href

        # Use robust URL normalization
        season_url = normalize_url(self.source.base_url, season_id)

        self.logger.debug("Fetching season episodes from: %s", season_url)
        res = await self.client.get(season_url)
        episode_elements = Document(res.body).select(
            "table.seasonEpisodesList tbody tr"
        )

        # Process episodes with concurrency limit
        return await self.async_pool(13, episode_elements, self.episode_from_element)

    async def episode_from_element(self, element: Any) -> dict[str, Any]:
        """Create episode from table row element.

        Args:
            element: Episode row element

        Returns:
            Episode dictionary with proper season/episode/title fields
        """
        title_anchor = element.select_first("td.seasonEpisodeTitle a")
        episode_span = title_anchor.select_first("span")
        url = title_anchor.attr("href")
        episode_season_id = element.attr("data-episode-season-id")

        episode_title = self.clean_html_string(self._safe_extract_text(episode_span))

        # Parse season and episode numbers from URL
        # Handle movies/films (supports both /filme/ and /film/)
        film_match = re.search(self.FILM_URL_PATTERN, url)
        if film_match:
            film_num = int(film_match.group(1))
            return {
                "name": f"Film {film_num} : {episode_title}",
                "url": url,
                "kind": "movie",
                "number": film_num,
                "title": episode_title,
            }

        # Handle regular episodes
        season_match = re.search(r"staffel-(\d+)/episode-(\d+)", url)
        if season_match:
            season_num = int(season_match.group(1))
            episode_num = int(season_match.group(2))
            name = f"Staffel {season_num} Folge {episode_num} : {episode_title}"

            return {
                "name": name,
                "url": url,
                "season": season_num,
                "episode": episode_num,
                "kind": "series",
                "title": episode_title,
            }

        # Fallback: try to extract from episode_season_id and URL
        try:
            episode_num = int(episode_season_id) if episode_season_id else 1
        except (ValueError, TypeError):
            episode_num = 1

        # Try to extract season from URL pattern
        season_match = re.search(r"staffel-(\d+)", url)
        season_num = int(season_match.group(1)) if season_match else 1

        name = f"Staffel {season_num} Folge {episode_num} : {episode_title}"

        return {
            "name": name,
            "url": url,
            "season": season_num,
            "episode": episode_num,
            "kind": "series",
            "title": episode_title,
        }

    # =========================================================================
    # Video Extraction
    # =========================================================================

    async def get_video_list(
        self, url: str, lang_filter: str | None = None
    ) -> VideoListResponse:
        """Get video sources for episode.

        Args:
            url: Episode URL
            lang_filter: Optional language filter (e.g., 'de', 'en'). If None, returns all sources.

        Returns:
            VideoListResponse with video sources
        """
        base_url = self.source.base_url
        if lang_filter and lang_filter != "all":
            self.logger.info(
                "Getting video list for %s with language filter: %s", url, lang_filter
            )
        else:
            lang_filter = None
            self.logger.info("Getting video list for %s", url)

        # Use robust URL normalization
        full_url = normalize_url(base_url, url)
        referer_url = full_url

        headers = {
            "Accept": "*/*",
            "Referer": referer_url,
            "Priority": "u=0, i",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        }
        self.logger.info("Getting video list for %s", full_url)
        res = await self.client.get(full_url, headers)
        document = Document(res.body)

        redirects_elements = document.select("ul.row li")
        self.logger.info("Found %d redirect elements", len(redirects_elements))

        # Create tasks for concurrent processing
        tasks = []
        for element in redirects_elements:
            langkey = element.attr("data-lang-key")
            # Map language keys correctly:
            # "1" = German Dub (Deutsch Dub)
            # "2" = English Sub (Englisch Sub)
            # "3" = German Sub (Deutsch Sub)
            if langkey == "1":
                lang = "Deutsch"
                type_str = "Dub"
            elif langkey == "2":
                lang = "Englisch"
                type_str = "Sub"
            elif langkey == "3":
                lang = "Deutsch"
                type_str = "Sub"
            else:
                # Fallback for unknown keys
                lang = "Unknown"
                type_str = "Unknown"

            host_element = element.select_first("a h4")
            host = self._safe_extract_text(host_element)

            # Apply language filter if specified
            lang_code = map_language_to_code(lang)
            if lang_filter and lang_code != lang_filter:
                self.logger.info(
                    "Skipping %s %s %s (filter: %s)", lang, type_str, host, lang_filter
                )
                continue

            self.logger.debug(
                "Processing: lang=%s, type=%s, host=%s", lang, type_str, host
            )

            redirect_element = element.select_first("a.watchEpisode")
            if redirect_element._element:
                redirect = self._build_full_url(redirect_element.attr("href"))
                task = self._extract_videos_from_host(
                    redirect, host, lang, type_str, headers
                )
                tasks.append(task)

        # Process all hosts concurrently
        if tasks:
            import asyncio

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Collect all successful video extractions
            videos = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error("Task failed: %s", result)
                elif result:  # result is a list of videos
                    videos.extend(result)
        else:
            videos = []

        return VideoListResponse(type=self.response_type, videos=videos)

    async def _extract_videos_from_host(
        self, redirect: str, host: str, lang: str, type_str: str, headers: dict
    ) -> list:
        """Extract videos from a single host asynchronously.

        Args:
            redirect: Redirect URL for the host
            host: Host name
            lang: Language (Deutsch/Englisch)
            type_str: Type (Dub/Sub)
            headers: HTTP headers to use

        Returns:
            List of extracted videos or empty list if failed
        """
        try:
            # Get the redirect URL manually by disabling auto-redirect
            async with httpx.AsyncClient(
                follow_redirects=False, timeout=30.0
            ) as no_redirect_client:
                redirect_response = await no_redirect_client.get(
                    redirect, headers=headers
                )

                # Get the redirect location
                location = redirect_response.headers.get("location")
                if not location:
                    self.logger.warning(
                        "No location header for %s. Status: %d",
                        host,
                        redirect_response.status_code,
                    )
                    return []

                self.logger.info("Extracting from %s: %s", host, location)

            # Extract videos using the appropriate extractor
            extracted_videos = await extract_any(
                location,
                host.lower(),
                headers={"Referer": self.source.base_url},
            )

            # Set language and type fields on all extracted videos
            lang_code = map_language_to_code(lang)
            for video in extracted_videos:
                video.language = lang_code
                video.type = type_str
                # Update quality label to include language, type, and host info
                if video.quality:
                    video.quality = f"{lang} {type_str} {video.quality} {host}"
                else:
                    video.quality = f"{lang} {type_str} {host}"

            self.logger.info("Extracted %d videos from %s", len(extracted_videos), host)

            return extracted_videos if extracted_videos else []

        except (httpx.HTTPError, ValueError, RuntimeError):
            # Log the error but don't raise it (handled by gather)
            self.logger.exception("Failed to extract from %s", host)
            return []

    # =========================================================================
    # Abstract Methods (must be implemented by subclasses)
    # =========================================================================

    @abstractmethod
    async def get_popular(self, page: int = 1) -> PaginatedSearchResultResponse:
        """Get popular media list.

        Args:
            page: Page number

        Returns:
            PaginatedSearchResultResponse with media list
        """

    @abstractmethod
    async def get_latest_updates(self, page: int = 1) -> PaginatedSearchResultResponse:
        """Get latest updates.

        Args:
            page: Page number

        Returns:
            PaginatedSearchResultResponse with media list
        """

    @abstractmethod
    async def search(
        self, query: str, page: int = 1, lang: str | None = None
    ) -> PaginatedSearchResultResponse:
        """Search for content.

        Args:
            query: Search query
            page: Page number
            lang: Optional language filter (de, en, sub, all)

        Returns:
            PaginatedSearchResultResponse with search results
        """

    @abstractmethod
    def get_source_preferences(self) -> list[SourcePreference]:
        """Get source preferences configuration.

        Returns:
            List of source preferences
        """
