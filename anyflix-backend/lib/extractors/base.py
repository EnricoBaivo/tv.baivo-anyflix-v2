"""Base extractor class for video sources."""

from abc import ABC, abstractmethod

from lib.models.base import VideoSource


class BaseExtractor(ABC):
    """Base class for video extractors."""

    @abstractmethod
    async def extract(
        self, url: str, headers: dict[str, str] | None = None
    ) -> list[VideoSource]:
        """Extract video sources from URL.

        Args:
            url: URL to extract from
            headers: Optional headers for requests

        Returns:
            List of video sources
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get extractor name."""
