"""SerienStream provider implementation."""

import re
from typing import Any

import httpx

from ..extractors.extract_any import extract_any
from ..models.base import (
    MediaInfo,
    MediaSource,
    SearchResult,
    SourcePreference,
)
from ..models.responses import (
    LatestResponse,
    PopularResponse,
    SearchResponse,
    VideoListResponse,
)
from ..utils.caching import ServiceCacheConfig, cached
from ..utils.logging_config import get_logger
from ..utils.parser import Document
from ..utils.url_utils import normalize_url
from .base import BaseProvider


def _map_language_to_code(lang: str) -> str:
    """
    Map language names to standard language codes.

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


class SerienStreamProvider(BaseProvider):
    """SerienStream series source provider."""

    # Maximum items per page for pagination
    ITEMS_PER_PAGE = 15

    def __init__(self):
        """Initialize SerienStream provider."""
        source = MediaSource(
            name="SerienStream",
            lang="de",
            base_url="https://serienstream.to",
            api_url="",
            icon_url="https://serienstream.to/favicon.ico",
            type_source="single",
            item_type=1,
            is_nsfw=False,
            version="0.0.9",
            date_format="",
            date_format_locale="",
            pkg_path="anime/src/de/serienstream.js",  # reference to the javascript file from mangayomi
        )
        super().__init__(source)
        self.logger = get_logger(__name__)
        self.logger.info(f"Initialized SerienStream provider: {source.base_url}")
        self.type = "normal"

    def _parse_series_list_elements(self, elements) -> list[SearchResult]:
        """Parse series list elements into SearchResult objects.

        Args:
            elements: DOM elements containing series data

        Returns:
            List of SearchResult objects
        """
        series_list = []

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

                series_list.append(
                    SearchResult(name=name, image_url=image_url, link=link)
                )

        return series_list

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

    def _build_full_url(self, path: str) -> str:
        """Build full URL from base URL and path.

        Args:
            path: URL path (can start with / or not)

        Returns:
            Full URL
        """
        base_url = self.source.base_url
        if path.startswith("http"):
            return path
        if path.startswith("/"):
            return base_url + path
        return f"{base_url}/{path}"

    def _safe_extract_text(self, element, default: str = "") -> str:
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

    def _safe_extract_attr(self, element, attr_name: str, default: str = "") -> str:
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

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_POPULAR_TTL, key_prefix="serienstream_popular"
    )
    async def get_popular(self, page: int = 1) -> PopularResponse:
        """Get popular series with pagination."""
        res = await self.client.get(f"{self.source.base_url}/beliebte-serien")
        elements = Document(res.body).select("div.seriesListContainer div")

        all_series = self._parse_series_list_elements(elements)
        paginated_series, has_next_page = self._apply_pagination(all_series, page)

        return PopularResponse(
            type=self.response_type, list=paginated_series, has_next_page=has_next_page
        )

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_LATEST_TTL, key_prefix="serienstream_latest"
    )
    async def get_latest_updates(self, page: int = 1) -> LatestResponse:
        """Get latest series updates from SerienStream with pagination."""
        res = await self.client.get(f"{self.source.base_url}/neu")
        elements = Document(res.body).select("div.seriesListContainer div")

        all_series = self._parse_series_list_elements(elements)
        paginated_series, has_next_page = self._apply_pagination(all_series, page)

        return LatestResponse(
            type=self.response_type, list=paginated_series, has_next_page=has_next_page
        )

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_SEARCH_TTL, key_prefix="serienstream_search"
    )
    async def search(
        self, query: str, page: int = 1, lang: str | None = None
    ) -> SearchResponse:
        """Search for series with pagination."""

        res = await self.client.get(f"{self.source.base_url}/serien")
        elements = Document(res.body).select("#seriesContainer > div > ul > li > a")

        # Filter and build results
        filtered_results = []
        for element in elements:
            if element._element:
                name = element.text
                if query.lower() in name.lower():
                    filtered_results.append(
                        SearchResult(name=name, image_url="", link=element.attr("href"))
                    )

        paginated_results, has_next_page = self._apply_pagination(
            filtered_results, page
        )
        return SearchResponse(
            type=self.response_type, list=paginated_results, has_next_page=has_next_page
        )

    def _extract_extended_metadata(self, document: Document, base_url: str):
        """Extract extended metadata from seriesContentBox.

        Args:
            document: Parsed HTML document
            base_url: Base URL for resolving relative URLs

        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}

        # Extract basic required fields
        # Extract name
        name_element = document.select_first("div.series-title h1 span")
        if name_element and name_element._element:
            metadata["name"] = name_element.text.strip()
        else:
            metadata["name"] = ""

        # Extract description
        desc_element = document.select_first("p.seri_des")
        if desc_element and desc_element._element:
            metadata["description"] = self.clean_html_string(
                desc_element.attr("data-full-description") or ""
            )
        else:
            metadata["description"] = ""

        # Extract cover image
        cover_element = document.select_first("div.seriesCoverBox img")
        if cover_element and cover_element._element:
            cover_path = cover_element.attr("data-src") or cover_element.attr("src")
            if cover_path:
                metadata["cover_image_url"] = self._build_full_url(cover_path)
            else:
                metadata["cover_image_url"] = ""
        else:
            metadata["cover_image_url"] = ""

        # Extract alternative titles
        title_element = document.select_first(
            "div.series-title h1[data-alternativeTitles]"
        )
        if title_element and title_element._element:
            alt_titles_str = title_element.attr("data-alternativeTitles")
            if alt_titles_str:
                # Split by comma and clean up
                alt_titles = [
                    title.strip()
                    for title in alt_titles_str.split(",")
                    if title.strip()
                ]
                metadata["alternative_titles"] = alt_titles

        # Extract years
        start_year_element = document.select_first('span[itemprop="startDate"] a')
        if start_year_element and start_year_element._element:
            try:
                metadata["start_year"] = int(start_year_element.text)
            except (ValueError, TypeError):
                pass

        end_year_element = document.select_first('span[itemprop="endDate"] a')
        if end_year_element and end_year_element._element:
            try:
                end_year_text = end_year_element.text
                if end_year_text != "Heute":  # "Today" in German
                    metadata["end_year"] = int(end_year_text)
            except (ValueError, TypeError):
                pass

        # Extract FSK rating
        fsk_element = document.select_first("div[data-fsk]")
        if fsk_element and fsk_element._element:
            try:
                metadata["fsk_rating"] = int(fsk_element.attr("data-fsk"))
            except (ValueError, TypeError):
                pass

        # Extract IMDB ID
        imdb_element = document.select_first("a[data-imdb]")
        if imdb_element and imdb_element._element:
            imdb_id = imdb_element.attr("data-imdb")
            if imdb_id:
                metadata["imdb_id"] = imdb_id

        # Extract country of origin
        country_element = document.select_first(
            'li[data-content-type="country"] span[itemprop="name"]'
        )
        if country_element and country_element._element:
            metadata["country_of_origin"] = country_element.text

        # Extract genres
        genre_elements = document.select("div.genres ul li")
        genres = []
        for elem in genre_elements:
            if elem._element:
                genre_name = elem.text.strip()
                # Filter out "+ X" patterns (e.g., "+ 1", "+ 5", etc.)
                if genre_name and not re.match(r"^\+\s*\d+$", genre_name):
                    genres.append(genre_name)
        if genres:
            metadata["genre"] = genres

        # Extract main genre
        main_genre_element = document.select_first("div.genres ul[data-main-genre]")
        if main_genre_element and main_genre_element._element:
            main_genre = main_genre_element.attr("data-main-genre")
            if main_genre:
                metadata["main_genre"] = main_genre

        # Extract directors
        director_elements = document.select("li.seriesDirector a span[itemprop='name']")
        directors = []
        for elem in director_elements:
            if elem._element:
                director_name = elem.text.strip()
                if director_name and not re.match(
                    r"^\s*&\s*\d+\s*weitere\s*$", director_name
                ):
                    directors.append(director_name)
        if directors:
            metadata["directors"] = directors

        # Extract actors
        actor_elements = document.select(
            "li .seriesActor ~ ul li span[itemprop='name']"
        )
        actors = []
        for elem in actor_elements:
            if elem._element:
                actor_name = elem.text.strip()
                if actor_name and not re.match(
                    r"^\s*&\s*\d+\s*weitere\s*$", actor_name
                ):
                    actors.append(actor_name)
        if actors:
            metadata["actors"] = actors

        # Extract producers
        producer_elements = document.select(
            "li .seriesProducer ~ ul li span[itemprop='name']"
        )
        producers = []
        for elem in producer_elements:
            if elem._element:
                producer_name = elem.text.strip()
                if producer_name and not re.match(
                    r"^\s*&\s*\d+\s*weitere\s*$", producer_name
                ):
                    producers.append(producer_name)
        if producers:
            metadata["producers"] = producers

        # Extract author/producer for compatibility
        if producers:
            metadata["author"] = ", ".join(producers[:3])  # Limit to first 3
        else:
            metadata["author"] = ""

        # Set default status
        metadata["status"] = 5

        # Extract backdrop URL
        backdrop_element = document.select_first("div.backdrop")
        if backdrop_element and backdrop_element._element:
            style = backdrop_element.attr("style")
            if style:
                # Extract URL from background-image style
                match = re.search(r"url\(([^)]+)\)", style)
                if match:
                    backdrop_path = match.group(1).strip("'\"")
                    metadata["backdrop_url"] = self._build_full_url(backdrop_path)

        # Extract series ID
        series_id_element = document.select_first("div.add-series[data-series-id]")
        if series_id_element and series_id_element._element:
            series_id = series_id_element.attr("data-series-id")
            if series_id:
                metadata["series_id"] = series_id

        return metadata

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_DETAIL_TTL, key_prefix="serienstream_detail"
    )
    async def get_detail(self, url: str):
        """Get series details from SerienStream.

        Args:
            url: Series URL

        Returns:
            MediaInfo with series details
        """
        # Use robust URL normalization
        full_url = normalize_url(self.source.base_url, url)

        self.logger.debug(f"Fetching series detail from: {full_url}")
        res = await self.client.get(full_url)
        document = Document(res.body)

        # Extract extended metadata (includes basic info)
        extended_metadata = self._extract_extended_metadata(
            document, self.source.base_url
        )

        # Extract episodes
        seasons_elements = document.select("#stream > ul:nth-child(1) > li > a")

        # Process seasons with concurrency limit
        episodes_arrays = await self.async_pool(
            2, seasons_elements, self.parse_episodes_from_series
        )

        # Flatten and reverse episodes
        episodes = []
        for ep_array in episodes_arrays:
            episodes.extend(ep_array)
        episodes.reverse()

        # Add episodes to the metadata and create MediaInfo
        extended_metadata["episodes"] = episodes

        return MediaInfo(**extended_metadata)

    async def parse_episodes_from_series(self, element) -> list[dict[str, Any]]:
        """Parse episodes from a season.

        Args:
            element: Season element

        Returns:
            List of episodes
        """
        season_id = element.get_href

        # Use robust URL normalization
        season_url = normalize_url(self.source.base_url, season_id)

        self.logger.debug(f"Fetching season episodes from: {season_url}")
        res = await self.client.get(season_url)
        episode_elements = Document(res.body).select(
            "table.seasonEpisodesList tbody tr"
        )

        # Process episodes with concurrency limit
        return await self.async_pool(13, episode_elements, self.episode_from_element)

    async def episode_from_element(self, element) -> dict[str, Any]:
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
        if "/film" in url:
            # Handle movies/films
            film_match = re.search(r"/film/film-(\d+)", url)
            film_num = int(film_match.group(1)) if film_match else 1
            return {
                "name": f"Film {film_num} : {episode_title}",
                "url": url,
                "date_upload": None,
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
                "date_upload": None,
                "season": season_num,
                "episode": episode_num,
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
            "date_upload": None,
            "season": season_num,
            "episode": episode_num,
            "title": episode_title,
        }

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_VIDEOS_TTL, key_prefix="serienstream_videos"
    )
    async def get_video_list(
        self, url: str, lang_filter: str | None = None
    ) -> VideoListResponse:
        """Get video sources for episode from SerienStream.

        Args:
            url: Episode URL
            lang_filter: Optional language filter (e.g., 'de', 'en'). If None, returns all sources.

        Returns:
            VideoListResponse with video sources
        """
        base_url = self.source.base_url
        if lang_filter and lang_filter != "all":
            self.logger.info(
                f"Getting video list for {url} with language filter: {lang_filter}"
            )
        else:
            lang_filter = None
            self.logger.info(f"Getting video list for {url}")

        # Use robust URL normalization
        full_url = normalize_url(base_url, url)
        referer_url = full_url

        headers = {
            "Accept": "*/*",
            "Referer": referer_url,
            "Priority": "u=0, i",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        }
        self.logger.info(f"Getting video list for {full_url}")
        res = await self.client.get(full_url, headers)
        document = Document(res.body)

        redirects_elements = document.select("ul.row li")
        self.logger.info(f"Found {len(redirects_elements)} redirect elements")

        # Create tasks for concurrent processing
        tasks = []
        for element in redirects_elements:
            langkey = element.attr("data-lang-key")
            # Map language keys correctly:
            # "1" = German Dub (Deutscher Dub)
            # "2" = English Sub (Englischer Sub)
            # "3" = German Sub (Deutscher Sub)
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
            lang_code = _map_language_to_code(lang)
            if lang_filter and lang_code != lang_filter:
                self.logger.info(
                    f"Skipping {lang} {type_str} {host} (filter: {lang_filter})"
                )
                continue

            self.logger.info(f"Processing: lang={lang}, type={type_str}, host={host}")

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
                    self.logger.error(f"Task failed: {result}")
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
                        f"No location header for {host}. Status: {redirect_response.status_code}"
                    )
                    return []

                self.logger.info(f"Extracting from {host}: {location}")

            # Extract videos using the appropriate extractor
            extracted_videos = await extract_any(
                location,
                host.lower(),
                headers={"Referer": self.source.base_url},
            )

            # Set language and type fields on all extracted videos
            lang_code = _map_language_to_code(lang)
            for video in extracted_videos:
                video.language = lang_code
                video.type = type_str
                # Update quality label to include language, type, and host info
                if video.quality:
                    video.quality = f"{lang} {type_str} {video.quality} {host}"
                else:
                    video.quality = f"{lang} {type_str} {host}"

            self.logger.info(f"Extracted {len(extracted_videos)} videos from {host}")

            return extracted_videos if extracted_videos else []

        except Exception as e:
            # Log the error but don't raise it (handled by gather)
            self.logger.error(f"Failed to extract from {host}: {e}")
            return []

    def get_source_preferences(self) -> list[SourcePreference]:
        """Get SerienStream source preferences.

        Returns:
            List of source preferences
        """
        languages = ["Deutsch", "Englisch"]
        language_values = ["Deutscher", "Englischer"]
        types = ["Dub", "Sub"]
        resolutions = ["1080p", "720p", "480p"]
        hosts = [
            "Doodstream",
            "Filemoon",
            "Luluvdo",
            "SpeedFiles",
            "Streamtape",
            "Vidoza",
            "VOE",
        ]

        language_filters = []
        for lang in language_values:
            for type_val in types:
                language_filters.append(f"{lang} {type_val}")

        return [
            SourcePreference(
                key="lang",
                list_preference={
                    "title": "Bevorzugte Sprache",
                    "summary": "Wenn verfügbar, wird diese Sprache ausgewählt. Priority = 0 (lower is better)",
                    "valueIndex": 0,
                    "entries": languages,
                    "entryValues": language_values,
                },
            ),
            SourcePreference(
                key="type",
                list_preference={
                    "title": "Bevorzugter Typ",
                    "summary": "Wenn verfügbar, wird dieser Typ ausgewählt. Priority = 1 (lower is better)",
                    "valueIndex": 0,
                    "entries": types,
                    "entryValues": types,
                },
            ),
            SourcePreference(
                key="res",
                list_preference={
                    "title": "Bevorzugte Auflösung",
                    "summary": "Wenn verfügbar, wird diese Auflösung ausgewählt. Priority = 2 (lower is better)",
                    "valueIndex": 0,
                    "entries": resolutions,
                    "entryValues": resolutions,
                },
            ),
            SourcePreference(
                key="host",
                list_preference={
                    "title": "Bevorzugter Hoster",
                    "summary": "Wenn verfügbar, wird dieser Hoster ausgewählt. Priority = 3 (lower is better)",
                    "valueIndex": 0,
                    "entries": hosts,
                    "entryValues": hosts,
                },
            ),
            SourcePreference(
                key="lang_filter",
                multi_select_list_preference={
                    "title": "Sprachen auswählen",
                    "summary": "Wähle aus welche Sprachen dir angezeigt werden sollen. Weniger streams zu laden beschleunigt den Start der Videos.",
                    "entries": language_filters,
                    "entryValues": language_filters,
                    "values": language_filters,
                },
            ),
            SourcePreference(
                key="host_filter",
                multi_select_list_preference={
                    "title": "Hoster auswählen",
                    "summary": "Wähle aus welche Hoster dir angezeigt werden sollen. Weniger streams zu laden beschleunigt den Start der Videos.",
                    "entries": hosts,
                    "entryValues": hosts,
                    "values": hosts,
                },
            ),
        ]
