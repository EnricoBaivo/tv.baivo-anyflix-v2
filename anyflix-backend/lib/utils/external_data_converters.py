"""Converters for external service data to structured models."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


def convert_tmdb_data(
    raw_data: Dict[str, Any],
) -> Optional[Union["TMDBMovieData", "TMDBTVData"]]:
    """Convert raw TMDB data to structured model.

    Args:
        raw_data: Raw TMDB data dictionary

    Returns:
        Structured TMDBMovieData or TMDBTVData, or None if conversion fails
    """
    if not raw_data or not isinstance(raw_data, dict):
        return None

    try:
        from ..models.external import TMDBMovieData, TMDBTVData

        media_type = raw_data.get("media_type")

        # If no media_type, try to infer from available fields
        if not media_type:
            if "title" in raw_data and "release_date" in raw_data:
                media_type = "movie"
            elif "name" in raw_data and "first_air_date" in raw_data:
                media_type = "tv"
            else:
                # Default to movie if we can't determine
                media_type = "movie"

        if media_type == "movie":
            return TMDBMovieData(**raw_data)
        else:
            return TMDBTVData(**raw_data)

    except Exception as e:
        logger.warning(f"Failed to convert TMDB data to structured model: {e}")
        # Return None to fall back to raw dict
        return None


def convert_anilist_data(raw_data: Dict[str, Any]) -> Optional["AniListMediaData"]:
    """Convert raw AniList data to structured model.

    Args:
        raw_data: Raw AniList data dictionary

    Returns:
        Structured AniListMediaData, or None if conversion fails
    """
    if not raw_data or not isinstance(raw_data, dict):
        return None

    try:
        from ..models.external import AniListMediaData

        return AniListMediaData(**raw_data)

    except Exception as e:
        logger.warning(f"Failed to convert AniList data to structured model: {e}")
        # Return None to fall back to raw dict
        return None


def safe_convert_tmdb_data(
    raw_data: Optional[Dict[str, Any]],
) -> Optional[Union["TMDBMovieData", "TMDBTVData", Dict[str, Any]]]:
    """Safely convert TMDB data, falling back to raw dict if structured conversion fails.

    Args:
        raw_data: Raw TMDB data dictionary or None

    Returns:
        Structured model, raw dict, or None
    """
    if not raw_data:
        return None

    structured = convert_tmdb_data(raw_data)
    return structured if structured is not None else raw_data


def safe_convert_anilist_data(
    raw_data: Optional[Dict[str, Any]],
) -> Optional[Union["AniListMediaData", Dict[str, Any]]]:
    """Safely convert AniList data, falling back to raw dict if structured conversion fails.

    Args:
        raw_data: Raw AniList data dictionary or None

    Returns:
        Structured model, raw dict, or None
    """
    if not raw_data:
        return None

    structured = convert_anilist_data(raw_data)
    return structured if structured is not None else raw_data
