"""Base provider class similar to JavaScript MProvider."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models.base import (
    AnimeInfo,
    AnimeSource,
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
from ..utils.client import HTTPClient
from ..utils.helpers import async_pool, clean_html_string


class BaseProvider(ABC):
    """Base class for anime source providers."""

    def __init__(self, source: AnimeSource):
        """Initialize provider with source configuration.

        Args:
            source: Source configuration
        """
        self.source = source
        self.client = HTTPClient()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    @abstractmethod
    async def get_popular(self, page: int = 1) -> PopularResponse:
        """Get popular anime list.

        Args:
            page: Page number

        Returns:
            PopularResponse with anime list
        """
        pass

    @abstractmethod
    async def get_latest_updates(self, page: int = 1) -> LatestResponse:
        """Get latest updates.

        Args:
            page: Page number

        Returns:
            LatestResponse with anime list
        """
        pass

    @abstractmethod
    async def search(
        self, query: str, page: int = 1, filters: Optional[Dict[str, Any]] = None
    ) -> SearchResponse:
        """Search for anime.

        Args:
            query: Search query
            page: Page number
            filters: Optional search filters

        Returns:
            SearchResponse with search results
        """
        pass

    @abstractmethod
    async def get_detail(self, url: str) -> DetailResponse:
        """Get anime details.

        Args:
            url: Anime URL

        Returns:
            DetailResponse with anime details
        """
        pass

    @abstractmethod
    async def get_video_list(
        self, url: str, lang_filter: Optional[str] = None
    ) -> VideoListResponse:
        """Get video sources for episode.

        Args:
            url: Episode URL
            lang_filter: Optional language filter (e.g., 'de', 'en'). If None, returns all sources.

        Returns:
            VideoListResponse with video sources
        """
        pass

    @abstractmethod
    def get_source_preferences(self) -> List[SourcePreference]:
        """Get source preferences configuration.

        Returns:
            List of source preferences
        """
        pass

    def clean_html_string(self, input_str: str) -> str:
        """Clean HTML string helper.

        Args:
            input_str: Input string to clean

        Returns:
            Cleaned string
        """
        return clean_html_string(input_str)

    async def async_pool(self, pool_limit: int, array: List, iterator_fn) -> List:
        """Async pool helper.

        Args:
            pool_limit: Maximum concurrent operations
            array: Items to process
            iterator_fn: Function to apply to each item

        Returns:
            List of results
        """
        return await async_pool(pool_limit, array, iterator_fn)
