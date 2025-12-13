"""SerienStream provider implementation."""

from lib.models.base import MediaSource, SearchResult, SourcePreference
from lib.models.responses import PaginatedSearchResultResponse
from lib.utils.caching import ServiceCacheConfig, cached
from lib.utils.parser import Document

from .base import BaseProvider


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
            pkg_path="anime/src/de/serienstream.js",
        )
        super().__init__(source)
        self.logger.info("Initialized SerienStream provider: %s", source.base_url)
        self.type = "normal"

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_POPULAR_TTL, key_prefix="serienstream_popular"
    )
    async def get_popular(self, page: int = 1) -> PaginatedSearchResultResponse:
        """Get popular series with pagination."""
        res = await self.client.get(f"{self.source.base_url}/beliebte-serien")
        elements = Document(res.body).select("div.seriesListContainer div")

        all_series = await self._parse_media_list_elements(elements)
        paginated_series, has_next_page = self._apply_pagination(all_series, page)
        return PaginatedSearchResultResponse(
            type=self.response_type,
            list=paginated_series,
            has_next_page=has_next_page,
        )

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_LATEST_TTL, key_prefix="serienstream_latest"
    )
    async def get_latest_updates(self, page: int = 1) -> PaginatedSearchResultResponse:
        """Get latest series updates from SerienStream with pagination."""
        res = await self.client.get(f"{self.source.base_url}/neu")
        elements = Document(res.body).select("div.seriesListContainer div")

        all_series = await self._parse_media_list_elements(elements)
        paginated_series, has_next_page = self._apply_pagination(all_series, page)
        return PaginatedSearchResultResponse(
            type=self.response_type,
            list=paginated_series,
            has_next_page=has_next_page,
        )

    @cached(
        ttl=ServiceCacheConfig.PROVIDER_SEARCH_TTL, key_prefix="serienstream_search"
    )
    async def search(
        self, query: str, page: int = 1, _lang: str | None = None
    ) -> PaginatedSearchResultResponse:
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
                        SearchResult(
                            name=name,
                            image_url="",
                            link=element.attr("href"),
                            provider=self.source.name,
                        )
                    )

        paginated_results, has_next_page = self._apply_pagination(
            filtered_results, page
        )
        return PaginatedSearchResultResponse(
            type=self.response_type,
            list=paginated_results,
            has_next_page=has_next_page,
        )

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

        language_filters = [
            f"{lang} {type_val}" for lang in language_values for type_val in types
        ]

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
