"""Base provider class similar to JavaScript MProvider."""

from abc import ABC, abstractmethod

from lib.models.anilist import MediaType
from lib.models.base import (
    MatchSource,
    MediaInfo,
    MediaSource,
    SearchResult,
    SourcePreference,
    TMDBMediaResult,
)
from lib.models.responses import (
    PaginatedSearchResultResponse,
    VideoListResponse,
)
from lib.services.anilist_service import AniListService
from lib.services.matching_service import MatchingService
from lib.services.tmdb_service import TMDBService
from lib.utils.caching import ServiceCacheConfig, cached
from lib.utils.client import HTTPClient
from lib.utils.helpers import async_pool, clean_html_string
from lib.utils.parser import Document
from lib.utils.url_utils import normalize_url


class BaseProvider(ABC):
    """Base class for anime source providers."""

    def __init__(self, source: MediaSource) -> None:
        """Initialize provider with source configuration.

        Args:
            source: Source configuration
        """
        self.source = source
        self.client = HTTPClient()
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

    @abstractmethod
    async def get_popular(self, page: int = 1) -> PaginatedSearchResultResponse:
        """Get popular anime list.

        Args:
            page: Page number

        Returns:
            PaginatedSearchResultResponse with anime list
        """

    @abstractmethod
    async def get_latest_updates(self, page: int = 1) -> PaginatedSearchResultResponse:
        """Get latest updates.

        Args:
            page: Page number

        Returns:
            PaginatedSearchResultResponse with anime list
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

    @cached(ttl=ServiceCacheConfig.PROVIDER_DETAIL_TTL, key_prefix="aniworld_detail")
    async def get_detail(self, url: str, episodes: bool = True) -> MediaInfo:
        """Get anime details from AniWorld.

        Args:
            url: Anime URL

        Returns:
            DetailResponse with anime details
        """
        # Use robust URL normalization
        full_url = normalize_url(self.source.base_url, url)

        self.logger.debug("Fetching anime detail from: %s", full_url)
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
        episodes = []
        for ep_array in episodes_arrays:
            episodes.extend(ep_array)
        episodes.reverse()

        # Add episodes to the metadata and create MediaInfo
        extended_metadata["episodes"] = episodes
        extended_metadata["seasons_length"] = seasons_length

        return MediaInfo(**extended_metadata)

    @abstractmethod
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

    @abstractmethod
    def get_source_preferences(self) -> list[SourcePreference]:
        """Get source preferences configuration.

        Returns:
            List of source preferences
        """

    def clean_html_string(self, input_str: str) -> str:
        """Clean HTML string helper.

        Args:
            input_str: Input string to clean

        Returns:
            Cleaned string
        """
        return clean_html_string(input_str)

    async def enrich_with_details(self, search_result: SearchResult) -> SearchResult:
        """Enrich SearchResult with detailed MediaInfo."""
        media_info = await self.get_detail(search_result.link, episodes=False)
        confident_anime_source = False
        best_match_anilist = None
        best_match_tmdb = None
        best_match_source = None
        confidence = 0
        async with TMDBService() as tmdb_service:
            tmdb_media_info = await tmdb_service.search_multi(query=search_result.name)
            best_match_tmdb, confidence = MatchingService.calculate_match_confidence(
                media_info, tmdb_media_info
            )
            if best_match_tmdb:
                # Get detailed information
                if best_match_tmdb.media_type == "movie":
                    details = await tmdb_service.get_movie_details(
                        best_match_tmdb.id,
                        append_to_response="videos,images,external_ids,status",
                    )
                else:
                    details = await tmdb_service.get_tv_details(
                        best_match_tmdb.id,
                        append_to_response="videos,images,external_ids,status",
                    )
                if confidence >= 0.9:
                    best_match_source = MatchSource.TMDB
        if self.is_anime_source or confidence < 0.7:
            async with AniListService() as anilist_service:
                anilist_media_info = await anilist_service.search_anime(
                    query=search_result.name,
                    alternative_titles=media_info.alternative_titles,
                )

                if anilist_media_info is not None:
                    best_match_anilist, confidence = (
                        MatchingService.calculate_match_confidence(
                            media_info, anilist_media_info
                        )
                    )
                    if best_match_anilist:
                        confident_anime_source = (
                            best_match_anilist.type == MediaType.ANIME
                        )

                    if confidence > 0.9:
                        best_match_source = MatchSource.ANILIST

            # final result
        return SearchResult(
            name=search_result.name,
            image_url=search_result.image_url,
            link=search_result.link,
            media_info=media_info,
            anilist_media_info=best_match_anilist,
            tmdb_media_info=TMDBMediaResult(
                media_result=best_match_tmdb,
                media_info=details,
            )
            if best_match_tmdb
            else None,
            best_match_source=best_match_source,
            confidence=confidence,
            is_anime=confident_anime_source or self.is_anime_source,
            provider=self.source.name,
        )

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
