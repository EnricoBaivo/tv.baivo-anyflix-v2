"""Series API router - dedicated endpoints for series operations."""

import logging
import os

import httpx
from fastapi import APIRouter, HTTPException, Path, Query

from lib.models.responses import (
    EpisodeResponse,
    MovieResponse,
    MoviesResponse,
    SeasonResponse,
    SeasonsResponse,
    SeriesDetailResponse,
)
from lib.providers.aniworld import AniWorldProvider
from lib.providers.base import BaseProvider
from lib.providers.serienstream import SerienStreamProvider
from lib.services.series_converter import SeriesConverterService
from lib.services.tmdb_enrichment_service import TMDBEnrichmentService
from lib.services.tmdb_service import TMDBService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sources",
    tags=["series-api"],
    responses={
        404: {"description": "Source not found"},
        500: {"description": "Internal server error"},
    },
)

# Initialize providers with proper typing
providers: dict[str, BaseProvider] = {
    "aniworld": AniWorldProvider(),
    "serienstream": SerienStreamProvider(),
}

# Initialize services
tmdb_service = TMDBService(api_key=os.getenv("TMDB_API_KEY", ""))
enrichment_service = TMDBEnrichmentService(tmdb_service)


def get_provider(source: str) -> BaseProvider:
    """Get provider by source name.

    Args:
        source: The source name (e.g., 'aniworld', 'serienstream')

    Returns:
        BaseProvider: The provider instance for the given source

    Raises:
        HTTPException: If the source is not found (404)
    """
    if source not in providers:
        raise HTTPException(status_code=404, detail=f"Source '{source}' not found")
    return providers[source]


@router.get(
    "/{source}/series",
    response_model=SeriesDetailResponse,
    response_model_exclude_none=True,
    summary="Get overall series data (overview, no full episode list)",
)
async def get_series_overview(
    source: str = Path(...),
    url: str = Query(...),
) -> SeriesDetailResponse:
    """Get series overview data without full episode list.

    This endpoint fetches basic series information including season/episode
    counts but not the full episode details. Use /series/seasons for
    full episode data.
    """
    provider = get_provider(source)

    # Step 1: Fetch from provider WITHOUT episodes (overview only)
    try:
        async with provider:
            detail_response = await provider.get_detail(url, episodes=False)
    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        logger.exception("Failed to get detail from provider %s", source)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch series data from {source}"
        ) from e

    # Step 2: Enrich with TMDB data (basic TV info)
    tmdb_detail = None
    match_confidence = None
    try:
        async with tmdb_service:
            _tmdb_match, tmdb_detail, match_confidence = (
                await enrichment_service.enrich_media_info(detail_response)
            )
    except (httpx.HTTPError, ValueError, RuntimeError):
        logger.exception("Failed to enrich with TMDB data, continuing without it")

    # Step 3: Convert to hierarchical structure (will have empty seasons)
    try:
        slug = url.split("/")[-1] if "/" in url else "unknown"
        series_detail = SeriesConverterService.convert_to_hierarchical(
            detail_response, slug=slug
        )
    except ValueError as e:
        logger.exception("Failed to convert series to hierarchical structure")
        raise HTTPException(
            status_code=500, detail="Failed to process series data structure"
        ) from e

    return SeriesDetailResponse(
        type=provider.response_type,
        series=series_detail,
        tmdb_data=tmdb_detail,
        match_confidence=match_confidence,
        length=detail_response.seasons_length,
    )


@router.get(
    "/{source}/series/seasons",
    response_model=SeasonsResponse,
    response_model_exclude_none=True,
    summary="Get all seasons with full episode data",
)
async def get_series_seasons(
    source: str = Path(...),
    url: str = Query(...),
) -> SeasonsResponse:
    """Get all seasons for a series with full episode details.

    This endpoint fetches the complete episode list organized by season.
    """
    provider = get_provider(source)

    # Step 1: Fetch from provider WITH episodes (full data)
    try:
        async with provider:
            detail_response = await provider.get_detail(url, episodes=True)
    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        logger.exception("Failed to get detail from provider %s", source)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch series data from {source}"
        ) from e

    # Step 2: Enrich with TMDB data
    tmdb_detail = None
    match_confidence = None
    try:
        async with tmdb_service:
            _tmdb_match, tmdb_detail, match_confidence = (
                await enrichment_service.enrich_media_info(detail_response)
            )
    except (httpx.HTTPError, ValueError, RuntimeError):
        logger.exception("Failed to enrich with TMDB data, continuing without it")

    # Step 3: Convert to hierarchical structure
    try:
        slug = url.split("/")[-1] if "/" in url else "unknown"
        series_detail = SeriesConverterService.convert_to_hierarchical(
            detail_response, slug=slug
        )
    except ValueError as e:
        logger.exception("Failed to convert series to hierarchical structure")
        raise HTTPException(
            status_code=500, detail="Failed to process series data structure"
        ) from e

    return SeasonsResponse(
        type=provider.response_type,
        seasons=series_detail.seasons,
        tmdb_data=tmdb_detail,
        match_confidence=match_confidence,
    )


@router.get(
    "/{source}/series/seasons/{season_num}",
    response_model=SeasonResponse,
    response_model_exclude_none=True,
    summary="Get specific season with TMDB season details",
)
async def get_series_season(
    source: str = Path(...),
    season_num: int = Path(..., ge=1),
    url: str = Query(...),
) -> SeasonResponse:
    """Get details for a specific season with targeted TMDB lookup.

    This endpoint fetches season-specific TMDB data including all episodes
    for that season only.
    """
    provider = get_provider(source)

    # Step 1: Fetch from provider WITH episodes
    try:
        async with provider:
            detail_response = await provider.get_detail(url, episodes=True)
    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        logger.exception("Failed to get detail from provider %s", source)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch series data from {source}"
        ) from e

    # Step 2: Get TMDB ID first via basic enrichment
    tmdb_detail = None
    tmdb_season = None
    try:
        async with tmdb_service:
            tmdb_match, tmdb_detail, _confidence = (
                await enrichment_service.enrich_media_info(detail_response)
            )
            # Step 3: If we have a TV match, fetch season-specific TMDB data
            if tmdb_match and tmdb_match.media_type == "tv":
                tmdb_season = await enrichment_service.enrich_season(
                    tmdb_match.id, season_num
                )
    except (httpx.HTTPError, ValueError, RuntimeError):
        logger.exception("Failed to enrich with TMDB data, continuing without it")

    # Step 4: Convert to hierarchical structure and find the season
    try:
        slug = url.split("/")[-1] if "/" in url else "unknown"
        series_detail = SeriesConverterService.convert_to_hierarchical(
            detail_response, slug=slug
        )
    except ValueError as e:
        logger.exception("Failed to convert series to hierarchical structure")
        raise HTTPException(
            status_code=500, detail="Failed to process series data structure"
        ) from e

    for season in series_detail.seasons:
        if season.season == season_num:
            return SeasonResponse(
                type=provider.response_type,
                tmdb_data=tmdb_detail,
                tmdb_season=tmdb_season,
                season=season,
            )

    raise HTTPException(status_code=404, detail=f"Season {season_num} not found")


@router.get(
    "/{source}/series/seasons/{season_num}/episodes/{episode_num}",
    response_model=EpisodeResponse,
    response_model_exclude_none=True,
    summary="Get specific episode with TMDB episode details",
)
async def get_series_episode(
    source: str = Path(...),
    season_num: int = Path(..., ge=1),
    episode_num: int = Path(..., ge=1),
    url: str = Query(...),
) -> EpisodeResponse:
    """Get details for a specific episode with targeted TMDB lookup.

    This endpoint fetches episode-specific TMDB data including videos,
    images, crew, and guest stars for that episode only.
    """
    provider = get_provider(source)

    # Step 1: Fetch from provider WITH episodes
    try:
        async with provider:
            detail_response = await provider.get_detail(url, episodes=True)
    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        logger.exception("Failed to get detail from provider %s", source)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch series data from {source}"
        ) from e

    # Step 2: Get TMDB ID first via basic enrichment
    tmdb_detail = None
    tmdb_episode = None
    try:
        async with tmdb_service:
            tmdb_match, tmdb_detail, _confidence = (
                await enrichment_service.enrich_media_info(detail_response)
            )
            # Step 3: If we have a TV match, fetch episode-specific TMDB data
            if tmdb_match and tmdb_match.media_type == "tv":
                tmdb_episode = await enrichment_service.enrich_episode(
                    tmdb_match.id, season_num, episode_num
                )
    except (httpx.HTTPError, ValueError, RuntimeError):
        logger.exception("Failed to enrich with TMDB data, continuing without it")

    # Step 4: Convert to hierarchical structure and find the episode
    try:
        slug = url.split("/")[-1] if "/" in url else "unknown"
        series_detail = SeriesConverterService.convert_to_hierarchical(
            detail_response, slug=slug
        )
    except ValueError as e:
        logger.exception("Failed to convert series to hierarchical structure")
        raise HTTPException(
            status_code=500, detail="Failed to process series data structure"
        ) from e

    for season in series_detail.seasons:
        if season.season == season_num:
            for episode in season.episodes:
                if episode.episode == episode_num:
                    return EpisodeResponse(
                        type=provider.response_type,
                        tmdb_data=tmdb_detail,
                        tmdb_episode=tmdb_episode,
                        episode=episode,
                    )
            raise HTTPException(
                status_code=404,
                detail=f"Episode {episode_num} not found in season {season_num}",
            )

    raise HTTPException(status_code=404, detail=f"Season {season_num} not found")


@router.get(
    "/{source}/series/movies",
    response_model=MoviesResponse,
    response_model_exclude_none=True,
    summary="Get all movies/OVAs for a series",
)
async def get_series_movies(
    source: str = Path(...),
    url: str = Query(...),
) -> MoviesResponse:
    """Get all movies, OVAs, and specials for a series."""
    provider = get_provider(source)

    # Fetch from provider WITH episodes to get movies
    try:
        async with provider:
            detail_response = await provider.get_detail(url, episodes=True)
    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        logger.exception("Failed to get detail from provider %s", source)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch series data from {source}"
        ) from e

    # Enrich with TMDB data
    tmdb_detail = None
    match_confidence = None
    try:
        async with tmdb_service:
            _tmdb_match, tmdb_detail, match_confidence = (
                await enrichment_service.enrich_media_info(detail_response)
            )
    except (httpx.HTTPError, ValueError, RuntimeError):
        logger.exception("Failed to enrich with TMDB data, continuing without it")

    # Convert to hierarchical structure
    try:
        slug = url.split("/")[-1] if "/" in url else "unknown"
        series_detail = SeriesConverterService.convert_to_hierarchical(
            detail_response, slug=slug
        )
    except ValueError as e:
        logger.exception("Failed to convert series to hierarchical structure")
        raise HTTPException(
            status_code=500, detail="Failed to process series data structure"
        ) from e

    return MoviesResponse(
        type=provider.response_type,
        movies=series_detail.movies,
        tmdb_data=tmdb_detail,
        match_confidence=match_confidence,
    )


@router.get(
    "/{source}/series/movies/{movie_num}",
    response_model=MovieResponse,
    response_model_exclude_none=True,
    summary="Get specific movie/OVA",
)
async def get_series_movie(
    source: str = Path(...),
    movie_num: int = Path(..., ge=1),
    url: str = Query(...),
) -> MovieResponse:
    """Get details for a specific movie, OVA, or special."""
    provider = get_provider(source)

    # Fetch from provider WITH episodes to get movies
    try:
        async with provider:
            detail_response = await provider.get_detail(url, episodes=True)
    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        logger.exception("Failed to get detail from provider %s", source)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch series data from {source}"
        ) from e

    # Enrich with TMDB data
    tmdb_detail = None
    match_confidence = None
    try:
        async with tmdb_service:
            _tmdb_match, tmdb_detail, match_confidence = (
                await enrichment_service.enrich_media_info(detail_response)
            )
    except (httpx.HTTPError, ValueError, RuntimeError):
        logger.exception("Failed to enrich with TMDB data, continuing without it")

    # Convert to hierarchical structure
    try:
        slug = url.split("/")[-1] if "/" in url else "unknown"
        series_detail = SeriesConverterService.convert_to_hierarchical(
            detail_response, slug=slug
        )
    except ValueError as e:
        logger.exception("Failed to convert series to hierarchical structure")
        raise HTTPException(
            status_code=500, detail="Failed to process series data structure"
        ) from e

    for movie in series_detail.movies:
        if movie.number == movie_num:
            return MovieResponse(
                type=provider.response_type,
                movie=movie,
                tmdb_data=tmdb_detail,
                match_confidence=match_confidence,
            )

    raise HTTPException(status_code=404, detail=f"Movie {movie_num} not found")
