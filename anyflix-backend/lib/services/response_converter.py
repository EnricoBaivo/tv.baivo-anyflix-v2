"""Media sources API router."""

import logging

from lib.models.base import SearchResult
from lib.models.media import (
    MediaFormat,
    MediaRanking,
    MediaSourceEnum,
    MediaSpotlight,
    MediaStatusEnum,
)
from lib.models.tmdb import TMDBVideoType, get_genres_by_ids


def get_base_information(media_item: SearchResult) -> tuple[str, str]:
    """Get base information for media spotlight."""
    title = media_item.media_info.name
    description = None
    if media_item.tmdb_media_info and media_item.tmdb_media_info.media_result:
        title = media_item.tmdb_media_info.media_result.title
        if not title:
            title = media_item.media_info.name
        if not title:
            title = media_item.tmdb_media_info.media_result.original_title
        description = media_item.tmdb_media_info.media_result.overview
    if not description:
        description = media_item.media_info.description
    return title, description


def get_media_source_type(media_item: SearchResult) -> MediaSourceEnum:
    """Get media source type."""
    return (
        MediaSourceEnum.MOVIE
        if media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result
        and media_item.tmdb_media_info.media_result.media_type == "movie"
        else MediaSourceEnum.SERIES
    )


def get_media_format(media_item: SearchResult) -> MediaFormat | None:
    """Get media format with intelligent fallback logic.

    Args:
        media_item: Search result containing media information

    Returns:
        MediaFormat or None if format cannot be determined
    """
    logger = logging.getLogger(__name__)

    # Priority 1: Map TMDB media_type to appropriate MediaFormat
    if media_item.tmdb_media_info and media_item.tmdb_media_info.media_result:
        tmdb_type = media_item.tmdb_media_info.media_result.media_type
        format_mapping = {
            "movie": MediaFormat.MOVIE,
            "tv": MediaFormat.TV,
            "season": MediaFormat.TV,  # Season is part of TV series
            "episode": MediaFormat.TV,  # Episode is part of TV series
        }

        if tmdb_type in format_mapping:
            mapped_format = format_mapping[tmdb_type]
            logger.debug("Using TMDB mapped format: %s -> %s", tmdb_type, mapped_format)
            return mapped_format

    # Priority 2: Intelligent inference based on media characteristics
    if media_item.media_info:
        # Check duration for format inference
        duration = getattr(media_item.media_info, "duration", None)
        if duration is not None:
            if duration <= 30:  # Very short content
                logger.debug("Inferred format: TV_SHORT based on duration")
                return MediaFormat.TV_SHORT
            if duration <= 60:  # Short content (likely TV episode)
                logger.debug("Inferred format: TV based on duration")
                return MediaFormat.TV
            if duration > 60:  # Long content (likely movie)
                logger.debug("Inferred format: MOVIE based on duration")
                return MediaFormat.MOVIE

        # Check episode count for format inference
        episode_count = getattr(media_item.media_info, "episode_count", None)
        if episode_count is not None:
            if episode_count == 1:
                logger.debug("Inferred format: MOVIE based on single episode")
                return MediaFormat.MOVIE
            if episode_count <= 6:
                logger.debug("Inferred format: OVA based on low episode count")
                return MediaFormat.OVA
            logger.debug("Inferred format: TV based on episode count")
            return MediaFormat.TV

    # Priority 3: Check if we have any format hints from the source
    if hasattr(media_item, "source_format") and media_item.source_format:
        logger.debug("Using source format hint: %s", media_item.source_format)
        return MediaFormat.TV

    title = media_item.media_info.name if media_item.media_info else "Unknown"
    logger.warning("Could not determine media format for: %s", title)
    return MediaFormat.TV


def build_tmdb_image_url(
    image_path: str | None, image_type: str = "backdrop", size: str | None = None
) -> str | None:
    """Build full TMDB image URL from image path.

    Args:
        image_path: The image path from TMDB (e.g., "/5z5n69xtBHFEUTaX7ORE0P6hrnx.png")
        image_type: Type of image - "backdrop", "poster", "profile", "logo", "still"
        size: Specific size to use, if None will use default for image type

    Returns:
        Full TMDB image URL or None if image_path is None/empty
    """
    if not image_path:
        return None

    # Remove leading slash if present
    if image_path.startswith("/"):
        image_path = image_path[1:]

    # Default sizes for different image types
    default_sizes = {
        "backdrop": "w1280",  # Standard backdrop size
        "poster": "w500",  # Standard poster size
        "profile": "w185",  # Standard profile size
        "logo": "w500",  # Standard logo size
        "still": "w300",  # Standard still size
    }

    # Use provided size or default for image type
    image_size = size or default_sizes.get(image_type, "original")

    # Build the full URL
    base_url = "https://image.tmdb.org/t/p/"
    return f"{base_url}{image_size}/{image_path}"


def get_image_cover_url(media_item: SearchResult) -> str:
    """Get image cover url. Prefer TMDB poster path and fallback to media info cover image url."""
    cover_image_url = media_item.media_info.cover_image_url
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result.poster_path is not None
    ):
        cover_image_url = build_tmdb_image_url(
            media_item.tmdb_media_info.media_result.poster_path, image_type="poster"
        )
    return cover_image_url


def get_image_backdrop_url(media_item: SearchResult) -> str:
    """Get image backdrop url with proper TMDB base URL construction."""
    backdrop_image_url = media_item.media_info.backdrop_url

    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result
        and media_item.tmdb_media_info.media_result.backdrop_path is not None
    ):
        backdrop_image_url = build_tmdb_image_url(
            media_item.tmdb_media_info.media_result.backdrop_path, image_type="backdrop"
        )

    return backdrop_image_url


def get_logo_urls(media_item: SearchResult) -> list[str]:
    """Get logo urls."""
    logo_urls = []
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_info
        and media_item.tmdb_media_info.media_info.images.logos is not None
    ):
        """
        "logos": [
                    {
                        "aspect_ratio": 1.99,
                        "height": 386,
                        "iso_639_1": "ja",
                        "file_path": "/5z5n69xtBHFEUTaX7ORE0P6hrnx.png",
                        "vote_average": 3.334,
                        "vote_count": 1,
                        "width": 768
                    }
                ],
        """
        logo_urls = [
            build_tmdb_image_url(logo.file_path, image_type="logo")
            for logo in media_item.tmdb_media_info.media_info.images.logos
        ]
        print("logo_urls", logo_urls)  #

    return logo_urls


def get_color(media_item: SearchResult) -> str:
    """Get color."""
    return None


def get_seasons_and_episodes_count(media_item: SearchResult) -> tuple[int, int]:
    """Get episodes count."""
    media_info = media_item.media_info
    seasons_count = None
    episodes_count = None
    if media_info.seasons_length is not None:
        seasons_count = media_info.seasons_length
    if media_info.episodes is not None:
        episodes_count = len(media_info.episodes)

    return seasons_count, episodes_count


def get_release_year(media_item: SearchResult) -> int:
    """Get release year."""
    release_year = media_item.media_info.end_year
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result
        and media_item.tmdb_media_info.media_result.release_date is not None
    ):
        release_year = media_item.tmdb_media_info.media_result.release_date.split("-")[
            0
        ]
    else:
        release_year = media_item.media_info.start_year
    return release_year


def get_average_rating(media_item: SearchResult) -> int:
    """Get average rating."""
    average_rating = 0
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result
        and media_item.tmdb_media_info.media_result.vote_average is not None
    ):
        average_rating = media_item.tmdb_media_info.media_result.vote_average
    return average_rating


def get_popularity(media_item: SearchResult) -> int:
    """Get popularity."""
    popularity = 0
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result
        and media_item.tmdb_media_info.media_result.popularity is not None
    ):
        popularity = media_item.tmdb_media_info.media_result.popularity
    return popularity


def get_votes(media_item: SearchResult) -> int:
    """Get votes."""
    votes = 0
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result
        and media_item.tmdb_media_info.media_result.vote_count is not None
    ):
        votes = media_item.tmdb_media_info.media_result.vote_count
    return votes


def get_media_status(media_item: SearchResult) -> MediaStatusEnum:
    """Get media status."""
    # TODO: add tmdb media status - needs additional fetching
    return MediaStatusEnum.RELEASED


def get_genres(media_item: SearchResult) -> list[str]:
    """Get genres."""
    genres = []
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result
        and media_item.tmdb_media_info.media_result.genre_ids is not None
    ):
        # Split TMDB genres that contain "&"
        tmdb_genres = get_genres_by_ids(
            media_item.tmdb_media_info.media_result.genre_ids
        )
        for genre in tmdb_genres:
            if "&" in genre:
                # Split by "&" and clean up each part
                split_genres = [g.strip().lower() for g in genre.split("&")]
                for split_genre in split_genres:
                    if split_genre not in genres:
                        genres.append(split_genre)
            else:
                if genre.lower() not in genres:
                    genres.append(genre.lower())

    return genres


def get_trailer(media_item: SearchResult) -> str:
    """Get trailer."""
    youtube_base_url = "https://www.youtube.com/watch?v="
    trailers = None
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_info
        and media_item.tmdb_media_info.media_info.videos
        and any(media_item.tmdb_media_info.media_info.videos.results)
    ):
        videos = media_item.tmdb_media_info.media_info.videos.results
        trailers = [
            f"{youtube_base_url}{video.key}"
            for video in videos
            if video.site == "YouTube" and video.type == TMDBVideoType.TRAILER
        ]
    return trailers


def get_clips(media_item: SearchResult) -> str:
    """Get clips."""
    youtube_base_url = "https://www.youtube.com/watch?v="
    clips = None
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_info
        and media_item.tmdb_media_info.media_info.videos
        and any(media_item.tmdb_media_info.media_info.videos.results)
    ):
        videos = media_item.tmdb_media_info.media_info.videos.results
        clips = [
            f"{youtube_base_url}{video.key}"
            for video in videos
            if video.site == "YouTube" and video.type == TMDBVideoType.CLIP
        ]
    return clips


def get_teasers(media_item: SearchResult) -> str:
    """Get teasers."""
    youtube_base_url = "https://www.youtube.com/watch?v="
    teasers = None
    if (
        media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_info
        and media_item.tmdb_media_info.media_info.videos
        and any(media_item.tmdb_media_info.media_info.videos.results)
    ):
        videos = media_item.tmdb_media_info.media_info.videos.results
        teasers = [
            f"{youtube_base_url}{video.key}"
            for video in videos
            if video.site == "YouTube" and video.type == TMDBVideoType.TEASER
        ]
    return teasers


def get_best_ranking(media_item: SearchResult) -> MediaRanking:
    """Get best ranking. Currently not available without anilist."""
    return None


def get_fsk_rating(media_item: SearchResult) -> int:
    """Get fsk rating."""
    fsk_rating = media_item.media_info.fsk_rating

    return fsk_rating or 16


def convert_to_media_spotlight(media_item: SearchResult) -> MediaSpotlight:
    """Convert latest updates list to unified media spotlight list."""
    # get relevant media id based on best match source
    media_id = (
        media_item.tmdb_media_info.media_result.id
        if media_item.tmdb_media_info
        and media_item.tmdb_media_info.media_result
        and media_item.tmdb_media_info.media_result.id
        else media_item.media_info.imdb_id or media_item.link
    )
    # get relevant media title and description based on best match source
    title, description = get_base_information(media_item)
    # get relevant media type based on best match source
    media_source_type = get_media_source_type(media_item)
    media_format = get_media_format(media_item)
    image_cover_url = get_image_cover_url(media_item)
    image_backdrop_url = get_image_backdrop_url(media_item)
    seasons_count, episodes_count = get_seasons_and_episodes_count(media_item)
    release_year = get_release_year(media_item)
    average_rating = get_average_rating(media_item)
    popularity = get_popularity(media_item)
    votes = get_votes(media_item)
    media_status = get_media_status(media_item)
    genres = get_genres(media_item)
    trailers = get_trailer(media_item)
    clips = get_clips(media_item)
    teasers = get_teasers(media_item)
    best_ranking = get_best_ranking(media_item)
    fsk_rating = get_fsk_rating(media_item)
    media_spotlight = MediaSpotlight(
        id=str(media_id),
        tmdb_id=media_item.tmdb_media_info.media_result.id
        if media_item.tmdb_media_info is not None
        and media_item.tmdb_media_info.media_result is not None
        else None,
        title=title,
        fsk_rating=fsk_rating,
        episodes_count=episodes_count,
        seasons_count=seasons_count,
        description=description,
        media_source_type=media_source_type,
        image_cover_url=image_cover_url,
        image_backdrop_url=image_backdrop_url,
        release_year=release_year,
        average_rating=average_rating,
        popularity=popularity,
        votes=votes,
        media_status=media_status,
        genres=genres,
        source=media_item.best_match_source,
        provider_url=media_item.link,
        provider=media_item.provider,
        trailers=trailers,
        clips=clips,
        teasers=teasers,
        best_ranking=best_ranking,
        media_format=media_format,
        color=get_color(media_item),
        logo_urls=get_logo_urls(media_item),
    )
    return media_spotlight
