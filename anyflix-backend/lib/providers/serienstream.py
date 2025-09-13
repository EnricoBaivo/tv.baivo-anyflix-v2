"""SerienStream provider implementation."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..extractors.extract_any import extract_any
from ..models.base import (
    MediaInfo,
    MediaSource,
    SearchResult,
    SourcePreference,
    VideoSource,
)
from ..models.responses import (
    DetailResponse,
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
    elif "englisch" in lang_lower or "english" in lang_lower:
        return "en"
    else:
        return "sub"  # Default fallback


class SerienStreamProvider(BaseProvider):
    """SerienStream series source provider."""

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

    async def get_popular(self, page: int = 1) -> PopularResponse:
        """Get popular series from SerienStream.

        Args:
            page: Page number (not used, SerienStream doesn't paginate)

        Returns:
            PopularResponse with series list
        """
        base_url = self.source.base_url
        res = await self.client.get(f"{base_url}/beliebte-serien")
        elements = Document(res.body).select("div.seriesListContainer div")

        series_list = []
        for element in elements:
            link_element = element.select_first("a")
            name_element = element.select_first("h3")
            img_element = link_element.select_first("img")

            if link_element._element and name_element._element and img_element._element:
                name = name_element.text
                image_url = base_url + img_element.attr("data-src")
                link = link_element.attr("href")

                series_list.append(
                    SearchResult(name=name, image_url=image_url, link=link)
                )

        return PopularResponse(
            type=self.response_type, list=series_list, has_next_page=False
        )

    async def get_latest_updates(self, page: int = 1) -> LatestResponse:
        """Get latest series updates from SerienStream.

        Args:
            page: Page number (not used, SerienStream doesn't paginate)

        Returns:
            LatestResponse with series list
        """
        base_url = self.source.base_url
        res = await self.client.get(f"{base_url}/neu")
        elements = Document(res.body).select("div.seriesListContainer div")

        series_list = []
        for element in elements:
            link_element = element.select_first("a")
            name_element = element.select_first("h3")
            img_element = link_element.select_first("img")

            if link_element._element and name_element._element and img_element._element:
                name = name_element.text
                image_url = base_url + img_element.attr("data-src")
                link = link_element.attr("href")

                series_list.append(
                    SearchResult(name=name, image_url=image_url, link=link)
                )

        return LatestResponse(
            type=self.response_type, list=series_list, has_next_page=False
        )

    async def search(
        self, query: str, page: int = 1, lang: Optional[str] = None
    ) -> SearchResponse:
        """Search for series on SerienStream.

        Args:
            query: Search query
            page: Page number (not used)
            lang: Optional language filter (de, en, sub, all) - not used in serienstream

        Returns:
            SearchResponse with search results
        """
        # Log language filter for debugging (not implemented for serienstream)
        if lang:
            self.logger.info(
                f"Search with language filter: {lang} (not implemented for serienstream)"
            )

        base_url = self.source.base_url
        res = await self.client.get(f"{base_url}/serien")
        elements = Document(res.body).select("#seriesContainer > div > ul > li > a")

        # Filter elements by query
        filtered_elements = []
        for element in elements:
            title = element.attr("title").lower()
            if query.lower() in title:
                filtered_elements.append(element)

        series_list = []
        for element in filtered_elements:
            name = element.text
            link = element.attr("href")

            # Get image from detail page
            try:
                detail_res = await self.client.get(base_url + link)
                detail_doc = Document(detail_res.body)
                img_element = detail_doc.select_first("div.seriesCoverBox img")
                img = img_element.attr("data-src") if img_element._element else ""
                image_url = base_url + img if img else ""

                series_list.append(
                    SearchResult(name=name, image_url=image_url, link=link)
                )
            except Exception:
                # Skip this entry if we can't get the image
                continue

        return SearchResponse(
            type=self.response_type, list=series_list, has_next_page=False
        )

    async def get_detail(self, url: str) -> DetailResponse:
        """Get series details from SerienStream.

        Args:
            url: Series URL

        Returns:
            DetailResponse with series details
        """
        base_url = self.source.base_url
        res = await self.client.get(base_url + url)
        document = Document(res.body)

        # Extract basic info
        image_element = document.select_first("div.seriesCoverBox img")
        image_url = (
            base_url + image_element.attr("data-src") if image_element._element else ""
        )

        name_element = document.select_first("div.series-title h1 span")
        name = name_element.text if name_element._element else ""

        # Extract genres
        genre_elements = document.select("div.genres ul li")
        genre = []
        for g in genre_elements:
            genre_text = g.text
            # Filter out "+X" entries
            if not re.match(r"^\+\s\d+$", genre_text):
                genre.append(genre_text)

        # Extract description
        desc_element = document.select_first("p.seri_des")
        description = ""
        if desc_element._element:
            description = self.clean_html_string(
                desc_element.attr("data-full-description")
            )

        # Extract author/producer
        producer_elements = document.select("div.cast li")
        author = ""
        for prod in producer_elements:
            if "Produzent:" in prod.outer_html:
                producer_items = prod.select("li")
                author_parts = []
                for item in producer_items:
                    text = item.text
                    if not re.match(r"^\s\&\s\d+\sweitere$", text):
                        author_parts.append(text)
                author = ", ".join(author_parts)
                break

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

        series_info = MediaInfo(
            name=name,
            image_url=image_url,
            description=description,
            author=author,
            status=5,
            genre=genre,
            episodes=episodes,
        )

        return DetailResponse(media=series_info)

    async def parse_episodes_from_series(self, element) -> List[Dict[str, Any]]:
        """Parse episodes from a season.

        Args:
            element: Season element

        Returns:
            List of episodes
        """
        season_id = element.get_href
        res = await self.client.get(self.source.base_url + season_id)
        episode_elements = Document(res.body).select(
            "table.seasonEpisodesList tbody tr"
        )

        # Process episodes with concurrency limit
        return await self.async_pool(13, episode_elements, self.episode_from_element)

    async def episode_from_element(self, element) -> Dict[str, Any]:
        """Create episode from table row element.

        Args:
            element: Episode row element

        Returns:
            Episode dictionary
        """
        title_anchor = element.select_first("td.seasonEpisodeTitle a")
        episode_span = title_anchor.select_first("span")
        url = title_anchor.attr("href")

        # Get upload date
        date_upload = await self.get_upload_date_from_episode(url)

        episode_season_id = element.attr("data-episode-season-id")
        episode_title = (
            self.clean_html_string(episode_span.text) if episode_span._element else ""
        )

        name = ""
        if "/film" in url:
            name = f"Film {episode_season_id} : {episode_title}"
        else:
            season_match = re.search(r"staffel-(\d+)/episode", url)
            if season_match:
                season_num = season_match.group(1)
                name = (
                    f"Staffel {season_num} Folge {episode_season_id} : {episode_title}"
                )

        if name and url:
            return {"name": name, "url": url, "date_upload": date_upload}
        else:
            return {"name": "", "url": "", "date_upload": None}

    async def get_upload_date_from_episode(self, url: str) -> str:
        """Get upload date from episode page.

        Args:
            url: Episode URL

        Returns:
            Date upload as string (milliseconds since epoch)
        """
        try:
            base_url = self.source.base_url
            res = await self.client.get(base_url + url)
            document = Document(res.body)

            date_element = document.select_first('strong[style="color: white;"]')
            if not date_element._element:
                return str(int(datetime.now().timestamp() * 1000))

            date_string = date_element.text
            if ", " not in date_string:
                return str(int(datetime.now().timestamp() * 1000))

            date_time_part = date_string.split(", ")[1]
            if " " not in date_time_part:
                return str(int(datetime.now().timestamp() * 1000))

            date_part, time_part = date_time_part.split(" ")

            # Parse date (DD.MM.YYYY)
            day, month, year = map(int, date_part.split("."))

            # Parse time (HH:MM)
            hours, minutes = map(int, time_part.split(":"))

            # Create datetime object
            dt = datetime(year, month, day, hours, minutes)

            # Handle DST (simplified - just check if date is in summer months)
            # This is a simplified version of the complex DST calculation in the JS code
            is_dst = (
                3 <= month <= 10
            )  # Rough approximation for Central European Summer Time

            # Adjust for timezone (CET/CEST)
            if is_dst:
                # CEST is UTC+2
                dt = dt.replace(tzinfo=None)  # Remove timezone info for now
            else:
                # CET is UTC+1
                dt = dt.replace(tzinfo=None)  # Remove timezone info for now

            # Convert to milliseconds since epoch
            timestamp_ms = int(dt.timestamp() * 1000)
            return str(timestamp_ms)

        except Exception:
            # Return current time if parsing fails
            return str(int(datetime.now().timestamp() * 1000))

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_VIDEOS_TTL, key_prefix="serienstream_videos"
    )
    async def get_video_list(
        self, url: str, lang_filter: Optional[str] = None
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
            host = host_element.text if host_element._element else ""

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
                redirect = base_url + redirect_element.attr("href")
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
    ) -> List:
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
            import httpx

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

    def get_source_preferences(self) -> List[SourcePreference]:
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
