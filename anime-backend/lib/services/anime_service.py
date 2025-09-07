"""Anime service for managing providers."""

import logging
from typing import Any, Dict, List, Optional

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


class AnimeService:
    """Service for managing anime providers."""

    def __init__(self):
        """Initialize anime service with available providers."""
        self.logger = get_logger(__name__)
        self.providers: Dict[str, BaseProvider] = {
            "aniworld": AniWorldProvider(),
            "serienstream": SerienStreamProvider(),
        }
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

    async def get_popular(self, source: str, page: int = 1) -> PopularResponse:
        """Get popular anime from source.

        Args:
            source: Source name
            page: Page number

        Returns:
            PopularResponse

        Raises:
            ValueError: If source not found
        """
        with timed_operation(f"get_popular({source}, page={page})", self.logger):
            provider = self.get_provider(source)
            if not provider:
                self.logger.error(f"Source '{source}' not found for get_popular")
                raise ValueError(f"Source '{source}' not found")

            async with provider:
                result = await provider.get_popular(page)
                self.logger.info(
                    f"Retrieved {len(result.anime)} popular anime from {source} (page {page})"
                )
                return result

    async def get_latest_updates(self, source: str, page: int = 1) -> LatestResponse:
        """Get latest updates from source.

        Args:
            source: Source name
            page: Page number

        Returns:
            LatestResponse

        Raises:
            ValueError: If source not found
        """
        provider = self.get_provider(source)
        if not provider:
            raise ValueError(f"Source '{source}' not found")

        async with provider:
            return await provider.get_latest_updates(page)

    async def search(
        self,
        source: str,
        query: str,
        page: int = 1,
        filters: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """Search for anime in source.

        Args:
            source: Source name
            query: Search query
            page: Page number
            filters: Optional search filters

        Returns:
            SearchResponse

        Raises:
            ValueError: If source not found
        """
        provider = self.get_provider(source)
        if not provider:
            raise ValueError(f"Source '{source}' not found")

        async with provider:
            return await provider.search(query, page, filters)

    async def get_detail(self, source: str, url: str) -> DetailResponse:
        """Get anime details from source.

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

    async def get_series_detail(self, source: str, url: str) -> SeriesDetailResponse:
        """Get hierarchical series detail from source.

        Args:
            source: Source name
            url: Anime URL

        Returns:
            SeriesDetailResponse with hierarchical structure

        Raises:
            ValueError: If source not found
        """
        provider = self.get_provider(source)
        if not provider:
            raise ValueError(f"Source '{source}' not found")

        async with provider:
            # Get flat detail response
            detail_response = await provider.get_detail(url)

            # Convert episodes to dict format for normalization
            episodes_data = [
                {"name": ep.name, "url": ep.url, "date_upload": ep.date_upload}
                for ep in detail_response.anime.episodes
            ]

            # Normalize to hierarchical structure
            series_detail = normalize_series_detail(
                {"episodes": episodes_data}, slug=self._extract_slug_from_url(url)
            )

            return SeriesDetailResponse(series=series_detail)

    def _extract_slug_from_url(self, url: str) -> str:
        """Extract slug from anime URL."""
        import re

        # Extract from URL pattern like /anime/stream/attack-on-titan or /anime/attack-on-titan
        match = re.search(r"/anime/(?:stream/)?([^/]+)", url)
        return match.group(1) if match else "unknown"

    async def get_video_list(
        self, source: str, url: str, preferred_lang: str = None
    ) -> VideoListResponse:
        """Get video sources from source with optional language preference.

        Args:
            source: Source name
            url: Episode URL
            preferred_lang: Preferred language (e.g., "de", "en")

        Returns:
            VideoListResponse

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
                # Pass the language filter to the provider
                result = await provider.get_video_list(url, preferred_lang)

                self.logger.info(
                    f"Retrieved {len(result.videos)} video sources from {source}"
                )
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
