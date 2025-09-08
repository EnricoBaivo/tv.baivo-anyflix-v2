"""Base extractor class for video sources."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ..models.base import VideoSource


class BaseExtractor(ABC):
    """Base class for video extractors."""

    @abstractmethod
    async def extract(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> List[VideoSource]:
        """Extract video sources from URL.

        Args:
            url: URL to extract from
            headers: Optional headers for requests

        Returns:
            List of video sources
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get extractor name."""
        pass
