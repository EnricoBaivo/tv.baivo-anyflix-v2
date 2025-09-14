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
from lib.services.anilist_service import AniListService
from lib.services.series_converter import SeriesConverterService
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
anilist_service = AniListService()
tmdb_service = TMDBService(api_key=os.getenv("TMDB_API_KEY", ""))  # Get from env


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
    summary="📺 Get Full Series Data",
)
async def get_series_detail(
    source: str = Path(...),
    url: str = Query(...),
) -> SeriesDetailResponse:
    """Get complete series data with hierarchical structure."""
    provider = get_provider(source)

    # Get flat detail response
    try:
        async with provider:
            detail_response = await provider.get_detail(url)
    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        logger.exception("Failed to get detail from provider %s", source)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch series data from {source}"
        ) from e

    # Convert to hierarchical structure using converter service
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
        type=provider.type,
        series=series_detail,
        length=len(detail_response.episodes),
    )


@router.get(
    "/{source}/series/seasons",
    response_model=SeasonsResponse,
    response_model_exclude_none=True,
    summary="📺 Get All Seasons",
)
async def get_series_seasons(
    source: str = Path(...),
    url: str = Query(...),
) -> SeasonsResponse:
    """Get all seasons for a series."""
    series_detail = await get_series_detail(source, url)
    return SeasonsResponse(
        type=series_detail.type,
        seasons=series_detail.series.seasons,
    )


@router.get(
    "/{source}/series/seasons/{season_num}",
    response_model=SeasonResponse,
    response_model_exclude_none=True,
    summary="📺 Get Specific Season",
)
async def get_series_season(
    source: str = Path(...),
    season_num: int = Path(..., ge=1),
    url: str = Query(...),
) -> SeasonResponse:
    """Get details for a specific season."""
    series_detail = await get_series_detail(source, url)

    for season in series_detail.series.seasons:
        if season.season == season_num:
            return SeasonResponse(
                type=series_detail.type,
                tmdb_data=series_detail.tmdb_data,
                anilist_data=series_detail.anilist_data,
                season=season,
            )

    raise HTTPException(status_code=404, detail=f"Season {season_num} not found")


@router.get(
    "/{source}/series/seasons/{season_num}/episodes/{episode_num}",
    response_model=EpisodeResponse,
    response_model_exclude_none=True,
    summary="📺 Get Specific Episode",
)
async def get_series_episode(
    source: str = Path(...),
    season_num: int = Path(..., ge=1),
    episode_num: int = Path(..., ge=1),
    url: str = Query(...),
) -> EpisodeResponse:
    """Get details for a specific episode."""
    series_detail = await get_series_detail(source, url)

    for season in series_detail.series.seasons:
        if season.season == season_num:
            for episode in season.episodes:
                if episode.episode == episode_num:
                    return EpisodeResponse(
                        type=series_detail.type,
                        tmdb_data=series_detail.tmdb_data,
                        anilist_data=series_detail.anilist_data,
                        match_confidence=series_detail.match_confidence,
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
    summary="📺 Get All Movies/OVAs",
)
async def get_series_movies(
    source: str = Path(...),
    url: str = Query(...),
) -> MoviesResponse:
    """Get all movies, OVAs, and specials for a series."""
    series_detail = await get_series_detail(source, url)
    return MoviesResponse(
        type=series_detail.type,
        movies=series_detail.series.movies,
        tmdb_data=series_detail.tmdb_data,
        anilist_data=series_detail.anilist_data,
        match_confidence=series_detail.match_confidence,
    )


@router.get(
    "/{source}/series/movies/{movie_num}",
    response_model=MovieResponse,
    response_model_exclude_none=True,
    summary="📺 Get Specific Movie/OVA",
)
async def get_series_movie(
    source: str = Path(...),
    movie_num: int = Path(..., ge=1),
    url: str = Query(...),
) -> MovieResponse:
    """Get details for a specific movie, OVA, or special."""
    series_detail = await get_series_detail(source, url)

    for movie in series_detail.series.movies:
        if movie.number == movie_num:
            return MovieResponse(
                type=series_detail.type,
                movie=movie,
                tmdb_data=series_detail.tmdb_data,
                anilist_data=series_detail.anilist_data,
                match_confidence=series_detail.match_confidence,
            )

    raise HTTPException(status_code=404, detail=f"Movie {movie_num} not found")
