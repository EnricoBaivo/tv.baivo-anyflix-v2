"""Trailer utility functions."""

import logging

logger = logging.getLogger(__name__)


def build_youtube_url(trailer_data: dict, source: str = "unknown") -> str | None:
    """
    Build a full YouTube URL from trailer data.

    Args:
        trailer_data: Dictionary containing trailer information
        source: Source of the data ("anilist" or "tmdb")

    Returns:
        Full YouTube URL or None if unable to build
    """
    try:
        if source == "anilist":
            # AniList trailer structure: {id: "video_id", site: "youtube", thumbnail: "..."}
            video_id = trailer_data.get("id")
            site = trailer_data.get("site", "").lower()

            if video_id and site == "youtube":
                return f"https://www.youtube.com/watch?v={video_id}"

        elif source == "tmdb":
            # TMDB video structure: {key: "video_id", site: "YouTube", ...}
            video_key = trailer_data.get("key")
            site = trailer_data.get("site", "").lower()

            if video_key and site == "youtube":
                return f"https://www.youtube.com/watch?v={video_key}"

        # Generic approach - try to find video ID in common fields
        video_id = trailer_data.get("id") or trailer_data.get("key")
        site = trailer_data.get("site", "").lower()

        if video_id and ("youtube" in site or "yt" in site):
            return f"https://www.youtube.com/watch?v={video_id}"

        logger.warning(
            f"Unable to build YouTube URL from {source} trailer data: {trailer_data}"
        )
        return None

    except Exception as e:
        logger.error(f"Error building YouTube URL from {source} data: {e}")
        return None


def extract_trailer_info(
    trailer_data: dict, source: str = "unknown"
) -> tuple[str | None, str | None]:
    """
    Extract trailer URL and site information.

    Args:
        trailer_data: Dictionary containing trailer information
        source: Source of the data ("anilist" or "tmdb")

    Returns:
        Tuple of (youtube_url, site)
    """
    youtube_url = build_youtube_url(trailer_data, source)
    site = trailer_data.get("site", "Unknown")

    return youtube_url, site
