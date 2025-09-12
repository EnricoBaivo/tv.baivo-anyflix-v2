"""Unified anime service for managing providers with optional metadata enrichment."""

from typing import Any, Dict, List, Optional, Union

from ..models.base import SourcePreference
from ..models.responses import (
    DetailResponse,
    LatestResponse,
    PopularResponse,
    SearchResponse,
    SeriesDetailResponse,
    VideoListResponse,
)
from ..providers.aniworld import AniWorldProvider
from ..providers.base import BaseProvider
from ..providers.serienstream import SerienStreamProvider
from ..utils.logging_config import get_logger, timed_operation
from ..utils.normalization import normalize_series_detail

# Enhanced response imports (optional)
try:
    from ..models.enhanced import (
        EnhancedDetailResponse,
        EnhancedLatestResponse,
        EnhancedMediaInfo,
        EnhancedPopularResponse,
        EnhancedSearchResponse,
        EnhancedSearchResult,
        EnhancedSeriesDetail,
        EnhancedSeriesDetailResponse,
        EnhancedVideoListResponse,
        MetadataStats,
    )
    from ..services.metadata_service import MetadataEnrichmentService

    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False


class AnimeService:
    """Unified service for managing anime providers with optional metadata enrichment."""

    def __init__(
        self,
        enable_metadata: bool = False,
        cache_maxsize: int = 1000,
        cache_ttl: int = 3600,
    ):
        """Initialize anime service with available providers.

        Args:
            enable_metadata: Whether to enable AniList metadata enrichment
            cache_maxsize: Maximum number of items to cache (default: 1000)
            cache_ttl: Time-to-live for cache entries in seconds (default: 3600 = 1 hour)
        """
        self.logger = get_logger(__name__)
        self.enable_metadata = enable_metadata and ENHANCED_FEATURES_AVAILABLE

        # Initialize providers
        self.providers: Dict[str, BaseProvider] = {
            "aniworld": AniWorldProvider(),
            "serienstream": SerienStreamProvider(),
        }

        # Initialize metadata service if enabled and available
        if self.enable_metadata and ENHANCED_FEATURES_AVAILABLE:
            self.metadata_service = MetadataEnrichmentService(
                cache_maxsize=cache_maxsize, cache_ttl=cache_ttl
            )
            self.logger.info(
                f"AnimeService initialized with metadata enrichment enabled "
                f"(cache: {cache_maxsize} items, {cache_ttl}s TTL)"
            )
        else:
            self.metadata_service = None
            if enable_metadata and not ENHANCED_FEATURES_AVAILABLE:
                self.logger.warning(
                    "Metadata enrichment requested but enhanced features not available"
                )
            self.logger.info(
                "AnimeService initialized with metadata enrichment disabled"
            )

        self.logger.info(
            f"Initialized AnimeService with providers: {list(self.providers.keys())}"
        )

    def get_available_sources(self) -> List[str]:
        """Get list of available source names.

        Returns:
            List of source names
        """
        return list(self.providers.keys())

    def get_provider(self, source: str) -> Optional[BaseProvider]:
        """Get provider by source name.

        Args:
            source: Source name

        Returns:
            Provider instance or None if not found
        """
        provider = self.providers.get(source)
        if provider:
            self.logger.debug(f"Found provider for source: {source}")
        else:
            self.logger.warning(f"No provider found for source: {source}")
        return provider

    def _calculate_metadata_coverage(self, results: List[Any]) -> float:
        """Calculate the percentage of results that have AniList metadata."""
        if not results:
            return 0.0

        with_metadata = sum(
            1
            for r in results
            if hasattr(r, "anilist_data") and r.anilist_data is not None
        )
        return (with_metadata / len(results)) * 100

    async def get_popular(
        self, source: str, page: int = 1, include_metadata: bool = None
    ) -> Union[PopularResponse, "EnhancedPopularResponse"]:
        """Get popular anime from source with optional metadata enrichment.

        Args:
            source: Source name
            page: Page number
            include_metadata: Override global metadata setting for this request

        Returns:
            PopularResponse or EnhancedPopularResponse

        Raises:
            ValueError: If source not found
        """
        with timed_operation(
            f"get_popular({source}, page={page}, metadata={include_metadata})",
            self.logger,
        ):
            provider = self.get_provider(source)
            if not provider:
                self.logger.error(f"Source '{source}' not found for get_popular")
                raise ValueError(f"Source '{source}' not found")

            async with provider:
                # Get original results
                result = await provider.get_popular(page)
                self.logger.info(
                    f"Retrieved {len(result.list)} popular anime from {source} (page {page})"
                )

                # Determine if we should enrich with metadata
                should_enrich = (
                    include_metadata
                    if include_metadata is not None
                    else self.enable_metadata
                )

                if (
                    should_enrich
                    and self.metadata_service
                    and ENHANCED_FEATURES_AVAILABLE
                ):
                    # Enrich with metadata
                    async with self.metadata_service:
                        enhanced_results = (
                            await self.metadata_service.enrich_search_results(
                                result.list
                            )
                        )

                    metadata_coverage = self._calculate_metadata_coverage(
                        enhanced_results
                    )
                    self.logger.info(
                        f"Enhanced results with {metadata_coverage:.1f}% metadata coverage"
                    )

                    return EnhancedPopularResponse(
                        list=enhanced_results,
                        has_next_page=result.has_next_page,
                        metadata_coverage=metadata_coverage,
                    )
                elif should_enrich and ENHANCED_FEATURES_AVAILABLE:
                    # Return basic enhanced results without metadata
                    basic_enhanced = [
                        EnhancedSearchResult(
                            name=item.name, image_url=item.image_url, link=item.link
                        )
                        for item in result.list
                    ]

                    return EnhancedPopularResponse(
                        list=basic_enhanced,
                        has_next_page=result.has_next_page,
                        metadata_coverage=0.0,
                    )
                else:
                    # Return basic response
                    return result

    async def get_latest_updates(
        self, source: str, page: int = 1, include_metadata: bool = None
    ) -> Union[LatestResponse, "EnhancedLatestResponse"]:
        """Get latest updates from source with optional metadata enrichment.

        Args:
            source: Source name
            page: Page number
            include_metadata: Override global metadata setting for this request

        Returns:
            LatestResponse or EnhancedLatestResponse

        Raises:
            ValueError: If source not found
        """
        with timed_operation(
            f"get_latest_updates({source}, page={page}, metadata={include_metadata})",
            self.logger,
        ):
            provider = self.get_provider(source)
            if not provider:
                raise ValueError(f"Source '{source}' not found")

            async with provider:
                # Get original results
                result = await provider.get_latest_updates(page)
                self.logger.info(
                    f"Retrieved {len(result.list)} latest updates from {source} (page {page})"
                )

                # Determine if we should enrich with metadata
                should_enrich = (
                    include_metadata
                    if include_metadata is not None
                    else self.enable_metadata
                )

                if (
                    should_enrich
                    and self.metadata_service
                    and ENHANCED_FEATURES_AVAILABLE
                ):
                    # Enrich with metadata
                    async with self.metadata_service:
                        enhanced_results = (
                            await self.metadata_service.enrich_search_results(
                                result.list
                            )
                        )

                    metadata_coverage = self._calculate_metadata_coverage(
                        enhanced_results
                    )

                    return EnhancedLatestResponse(
                        list=enhanced_results,
                        has_next_page=result.has_next_page,
                        metadata_coverage=metadata_coverage,
                    )
                elif should_enrich and ENHANCED_FEATURES_AVAILABLE:
                    # Return basic enhanced results without metadata
                    basic_enhanced = [
                        EnhancedSearchResult(
                            name=item.name, image_url=item.image_url, link=item.link
                        )
                        for item in result.list
                    ]

                    return EnhancedLatestResponse(
                        list=basic_enhanced,
                        has_next_page=result.has_next_page,
                        metadata_coverage=0.0,
                    )
                else:
                    # Return basic response
                    return result

    async def search(
        self,
        source: str,
        query: str,
        page: int = 1,
        lang: Optional[str] = None,
        include_metadata: bool = None,
    ) -> Union[SearchResponse, "EnhancedSearchResponse"]:
        """Search for anime with optional metadata enrichment.

        Args:
            source: Source name
            query: Search query
            page: Page number
            lang: Optional language filter (de, en, sub, all)
            include_metadata: Override global metadata setting for this request

        Returns:
            SearchResponse or EnhancedSearchResponse

        Raises:
            ValueError: If source not found
        """
        with timed_operation(
            f"search({source}, '{query}', page={page}, metadata={include_metadata})",
            self.logger,
        ):
            provider = self.get_provider(source)
            if not provider:
                raise ValueError(f"Source '{source}' not found")

            async with provider:
                # Get original results
                result = await provider.search(query, page, lang)
                self.logger.info(
                    f"Found {len(result.list)} search results for '{query}' from {source}"
                )

                # Determine if we should enrich with metadata
                should_enrich = (
                    include_metadata
                    if include_metadata is not None
                    else self.enable_metadata
                )

                if (
                    should_enrich
                    and self.metadata_service
                    and ENHANCED_FEATURES_AVAILABLE
                ):
                    # Enrich with metadata
                    async with self.metadata_service:
                        enhanced_results = (
                            await self.metadata_service.enrich_search_results(
                                result.list
                            )
                        )

                    metadata_coverage = self._calculate_metadata_coverage(
                        enhanced_results
                    )

                    return EnhancedSearchResponse(
                        list=enhanced_results,
                        has_next_page=result.has_next_page,
                        metadata_coverage=metadata_coverage,
                        total_results=len(enhanced_results),
                    )
                elif should_enrich and ENHANCED_FEATURES_AVAILABLE:
                    # Return basic enhanced results without metadata
                    basic_enhanced = [
                        EnhancedSearchResult(
                            name=item.name, image_url=item.image_url, link=item.link
                        )
                        for item in result.list
                    ]

                    return EnhancedSearchResponse(
                        list=basic_enhanced,
                        has_next_page=result.has_next_page,
                        metadata_coverage=0.0,
                        total_results=len(basic_enhanced),
                    )
                else:
                    # Return basic response
                    return result

    async def _get_detail(self, source: str, url: str) -> DetailResponse:
        """Get anime details from source (internal use only).

        Args:
            source: Source name
            url: Anime URL

        Returns:
            DetailResponse

        Raises:
            ValueError: If source not found
        """
        provider = self.get_provider(source)
        if not provider:
            raise ValueError(f"Source '{source}' not found")

        async with provider:
            return await provider.get_detail(url)

    async def get_detail(
        self, source: str, url: str, include_metadata: bool = None
    ) -> Union[DetailResponse, "EnhancedDetailResponse"]:
        """Get anime details with optional metadata enrichment.

        Args:
            source: Source name
            url: Anime URL
            include_metadata: Override global metadata setting for this request

        Returns:
            DetailResponse or EnhancedDetailResponse

        Raises:
            ValueError: If source not found
        """
        with timed_operation(
            f"get_detail({source}, {url}, metadata={include_metadata})", self.logger
        ):
            provider = self.get_provider(source)
            if not provider:
                raise ValueError(f"Source '{source}' not found")

            async with provider:
                # Get original detail
                result = await provider.get_detail(url)
                self.logger.info(
                    f"Retrieved details for '{result.anime.name}' from {source}"
                )

                # Determine if we should enrich with metadata
                should_enrich = (
                    include_metadata
                    if include_metadata is not None
                    else self.enable_metadata
                )

                if (
                    should_enrich
                    and self.metadata_service
                    and ENHANCED_FEATURES_AVAILABLE
                ):
                    # Enrich with metadata
                    async with self.metadata_service:
                        enhanced_media = await self.metadata_service.enrich_media_info(
                            result.anime.name,
                            {
                                "image_url": result.anime.image_url,
                                "description": result.anime.description,
                                "author": result.anime.author,
                                "status": result.anime.status,
                                "genre": result.anime.genre,
                            },
                        )

                    return EnhancedDetailResponse(media=enhanced_media)
                elif should_enrich and ENHANCED_FEATURES_AVAILABLE:
                    # Return basic enhanced result without metadata
                    enhanced_media = EnhancedMediaInfo(
                        name=result.anime.name,
                        image_url=result.anime.image_url,
                        description=result.anime.description,
                        author=result.anime.author,
                        status=result.anime.status,
                        genre=result.anime.genre,
                    )

                    return EnhancedDetailResponse(media=enhanced_media)
                else:
                    # Return basic response
                    return result

    async def get_series_detail(
        self, source: str, url: str, include_metadata: bool = None
    ) -> Union[SeriesDetailResponse, "EnhancedSeriesDetailResponse"]:
        """Get hierarchical series detail with optional metadata enrichment.

        Args:
            source: Source name
            url: Anime URL
            include_metadata: Override global metadata setting for this request

        Returns:
            SeriesDetailResponse or EnhancedSeriesDetailResponse with hierarchical structure

        Raises:
            ValueError: If source not found
        """
        with timed_operation(
            f"get_series_detail({source}, {url}, metadata={include_metadata})",
            self.logger,
        ):
            provider = self.get_provider(source)
            if not provider:
                raise ValueError(f"Source '{source}' not found")

            # Get flat detail response using internal method
            async with provider:
                detail_response = await provider.get_detail(url)

            # Convert episodes to dict format for normalization
            media_info = detail_response.media
            episodes_data = media_info.episodes

            # Normalize to hierarchical structure
            slug = self._extract_slug_from_url(url)
            series_detail = normalize_series_detail(
                {"episodes": episodes_data}, slug=slug
            )

            # Determine if we should enrich with metadata
            should_enrich = (
                include_metadata
                if include_metadata is not None
                else self.enable_metadata
            )

            if should_enrich and self.metadata_service and ENHANCED_FEATURES_AVAILABLE:
                # Enrich with metadata
                async with self.metadata_service:
                    enhanced_series = await self.metadata_service.enrich_series_detail(
                        slug,
                        {
                            "name": media_info.name,
                            "seasons": series_detail.seasons,
                            "movies": series_detail.movies,
                        },
                    )

                return EnhancedSeriesDetailResponse(series=enhanced_series)
            elif should_enrich and ENHANCED_FEATURES_AVAILABLE:
                # Return basic enhanced result without metadata
                enhanced_series = EnhancedSeriesDetail(
                    slug=slug,
                    seasons=series_detail.seasons,
                    movies=series_detail.movies,
                )

                return EnhancedSeriesDetailResponse(series=enhanced_series)
            else:
                # Return basic response
                return SeriesDetailResponse(series=series_detail)

    def _extract_slug_from_url(self, url: str) -> str:
        """Extract slug from anime URL."""
        import re

        # Extract from URL pattern like /anime/stream/attack-on-titan or /anime/attack-on-titan
        match = re.search(r"/anime/(?:stream/)?([^/]+)", url)
        return match.group(1) if match else "unknown"

    async def get_video_list(
        self,
        source: str,
        url: str,
        preferred_lang: str = None,
        include_context: bool = False,
    ) -> Union[VideoListResponse, "EnhancedVideoListResponse"]:
        """Get video sources with optional anime context.

        Args:
            source: Source name
            url: Episode URL
            preferred_lang: Preferred language (e.g., "de", "en")
            include_context: Whether to include anime/episode context information

        Returns:
            VideoListResponse or EnhancedVideoListResponse

        Raises:
            ValueError: If source not found
        """
        with timed_operation(
            f"get_video_list({source}, {url}, {preferred_lang})", self.logger
        ):
            provider = self.get_provider(source)
            if not provider:
                self.logger.error(f"Source '{source}' not found for get_video_list")
                raise ValueError(f"Source '{source}' not found")

            async with provider:
                self.logger.info(f"Getting video list for {url} from source {source}")
                result = await provider.get_video_list(url, preferred_lang)

                self.logger.info(
                    f"Retrieved {len(result.videos)} video sources from {source}"
                )

                if include_context and ENHANCED_FEATURES_AVAILABLE:
                    # Prepare enhanced response with context
                    enhanced_response = EnhancedVideoListResponse(videos=result.videos)

                    # Extract anime and episode info from URL
                    import re

                    # Try to extract anime name and episode info from URL
                    anime_match = re.search(r"/anime/stream/([^/]+)", url)
                    episode_match = re.search(
                        r"/(staffel|season)-(\d+)/episode-(\d+)", url
                    )

                    if anime_match:
                        anime_name = anime_match.group(1).replace("-", " ").title()
                        enhanced_response.anime_context = {
                            "name": anime_name,
                            "slug": anime_match.group(1),
                        }

                    if episode_match:
                        enhanced_response.episode_context = {
                            "season": int(episode_match.group(2)),
                            "episode": int(episode_match.group(3)),
                        }

                    return enhanced_response
                else:
                    # Return basic response
                    return result

    def get_source_preferences(self, source: str) -> List[SourcePreference]:
        """Get source preferences.

        Args:
            source: Source name

        Returns:
            List of source preferences

        Raises:
            ValueError: If source not found
        """
        provider = self.get_provider(source)
        if not provider:
            raise ValueError(f"Source '{source}' not found")

        return provider.get_source_preferences()

    # Enhanced service methods (available when enhanced features are enabled)
    def get_metadata_stats(self) -> Optional["MetadataStats"]:
        """Get metadata enrichment statistics."""
        if self.metadata_service and ENHANCED_FEATURES_AVAILABLE:
            return self.metadata_service.get_stats()
        return None

    def get_cache_info(self) -> Optional[Dict[str, any]]:
        """Get cache information and statistics."""
        if self.metadata_service and ENHANCED_FEATURES_AVAILABLE:
            return self.metadata_service.get_cache_info()
        return None

    def clear_metadata_cache(self):
        """Clear the metadata cache."""
        if self.metadata_service and ENHANCED_FEATURES_AVAILABLE:
            self.metadata_service.clear_cache()
        else:
            self.logger.warning("Cannot clear cache: metadata service not available")

    def resize_metadata_cache(self, maxsize: int):
        """Resize the metadata cache."""
        if self.metadata_service and ENHANCED_FEATURES_AVAILABLE:
            self.metadata_service.resize_cache(maxsize)
        else:
            self.logger.warning("Cannot resize cache: metadata service not available")

    def set_cache_ttl(self, ttl: int):
        """Set cache TTL (time-to-live) in seconds."""
        if self.metadata_service and ENHANCED_FEATURES_AVAILABLE:
            self.metadata_service.set_cache_ttl(ttl)
        else:
            self.logger.warning("Cannot set cache TTL: metadata service not available")

    def set_metadata_enabled(self, enabled: bool):
        """Enable or disable metadata enrichment."""
        if ENHANCED_FEATURES_AVAILABLE:
            self.enable_metadata = enabled
            self.logger.info(
                f"Metadata enrichment {'enabled' if enabled else 'disabled'}"
            )
        else:
            self.logger.warning(
                "Cannot change metadata setting: enhanced features not available"
            )

    def is_enhanced_features_available(self) -> bool:
        """Check if enhanced features are available."""
        return ENHANCED_FEATURES_AVAILABLE

    def is_metadata_enabled(self) -> bool:
        """Check if metadata enrichment is enabled."""
        return self.enable_metadata and ENHANCED_FEATURES_AVAILABLE

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.metadata_service and ENHANCED_FEATURES_AVAILABLE:
            await self.metadata_service.__aexit__(exc_type, exc_val, exc_tb)
