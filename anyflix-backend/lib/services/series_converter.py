"""Series conversion service for transforming flat episode data into hierarchical structure."""

import logging

from lib.models.base import MediaInfo, SeriesDetail
from lib.utils.normalization import normalize_series_detail

logger = logging.getLogger(__name__)


class SeriesConverterService:
    """Service for converting flat episode data to hierarchical series structure."""

    @staticmethod
    def convert_to_hierarchical(
        detail_response: MediaInfo, slug: str | None = None
    ) -> SeriesDetail:
        """Convert flat DetailResponse to hierarchical SeriesDetail structure.

        Args:
            detail_response: DetailResponse with flat episode data
            slug: Optional slug override, if not provided will extract from URL

        Returns:
            SeriesDetail with episodes organized by seasons and movies

        Raises:
            ValueError: If episode data is invalid or cannot be processed
        """
        # Create flat_data structure expected by normalize_series_detail
        flat_data = {"episodes": detail_response.episodes}

        # Use the existing normalization utility which has advanced German parsing
        return normalize_series_detail(flat_data, slug=slug)
