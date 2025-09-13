"""Series conversion service for transforming flat episode data into hierarchical structure."""

import logging
from typing import Optional

from ..models.base import SeriesDetail
from ..models.responses import DetailResponse
from ..utils.normalization import normalize_series_detail

logger = logging.getLogger(__name__)


class SeriesConverterService:
    """Service for converting flat episode data to hierarchical series structure."""

    @staticmethod
    def convert_to_hierarchical(
        detail_response: DetailResponse, slug: Optional[str] = None
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
        try:
            # Create flat_data structure expected by normalize_series_detail
            flat_data = {"episodes": detail_response.media.episodes}

            # Use the existing normalization utility which has advanced German parsing
            return normalize_series_detail(flat_data, slug=slug)

        except Exception as e:
            logger.error(f"Failed to convert series to hierarchical structure: {e}")
            raise ValueError(f"Series conversion failed: {e}")
