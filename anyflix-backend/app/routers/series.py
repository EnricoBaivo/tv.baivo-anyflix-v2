"""Series API router - refactored with unified enrichment service."""

import logging

import httpx
from fastapi import APIRouter, HTTPException, Path, Query

from app.providers import enrichment_service, get_provider, tmdb_service
from lib.models.responses import (
    EpisodeResponse,
    MovieResponse,
    MoviesResponse,
    SeasonResponse,
    SeasonsResponse,
    SeriesDetailResponse,
)
from lib.services.series_enrichment_service import (
    EnrichedSeriesData,
    SeriesEnrichmentService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sources",
    tags=["series-api"],
    responses={
        404: {"description": "Source not found"},
        500: {"description": "Internal server error"},
    },
)

# Initialize the unified enrichment service
series_enrichment_service = SeriesEnrichmentService(enrichment_service)


# ============================================================================
# Helper Functions
# ============================================================================


async def fetch_series_with_enrichment(
    source: str,
    url: str,
    fetch_episodes: bool = True,
) -> EnrichedSeriesData:
    """Fetch series from provider with TMDB enrichment.

    Common workflow for all endpoints:
    1. Get provider instance
    2. Fetch and enrich series data
    3. Handle errors gracefully

    Args:
        source: Provider source name
        url: Series URL
        fetch_episodes: Whether to fetch full episode list

    Returns:
        EnrichedSeriesData

    Raises:
        HTTPException: On provider or processing errors
    """
    provider = get_provider(source)

    try:
        async with provider:
            async with tmdb_service:
                return await series_enrichment_service.fetch_and_enrich_series(
                    provider=provider,
                    url=url,
                    fetch_episodes=fetch_episodes,
                )
    except httpx.HTTPError as e:
        logger.exception("Failed to fetch from provider %s", source)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch series data from {source}",
        ) from e
    except (ValueError, RuntimeError) as e:
        logger.exception("Failed to process series data")
        raise HTTPException(
            status_code=500,
            detail="Failed to process series data structure",
        ) from e


# ============================================================================
# Endpoints
# ============================================================================


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
    enriched_data = await fetch_series_with_enrichment(
        source=source,
        url=url,
        fetch_episodes=False,
    )

    provider = get_provider(source)

    return SeriesDetailResponse(
        content_type=provider.content_type,
        series=enriched_data.series_detail,
        season_count=len(enriched_data.series_detail.seasons),
        # New structure
        tmdb_series_data=enriched_data.tmdb_tv_detail,
        match_confidence=enriched_data.match_confidence,
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

    This endpoint fetches the complete episode list organized by season,
    with TMDB data embedded in each season and episode.
    """
    enriched_data = await fetch_series_with_enrichment(
        source=source,
        url=url,
        fetch_episodes=True,
    )

    provider = get_provider(source)

    # Enrich all seasons with TMDB data if we have a TMDB ID
    if enriched_data.tmdb_id:
        try:
            async with tmdb_service:
                enriched_seasons = (
                    await series_enrichment_service.enrich_all_seasons_with_tmdb(
                        seasons=enriched_data.series_detail.seasons,
                        tmdb_id=enriched_data.tmdb_id,
                    )
                )
        except (httpx.HTTPError, ValueError, RuntimeError):
            logger.exception(
                "Failed to enrich seasons with TMDB data, using basic enrichment"
            )
            enriched_seasons = await series_enrichment_service.build_enriched_seasons(
                series_detail=enriched_data.series_detail,
                tmdb_id=enriched_data.tmdb_id,
                tmdb_tv_detail=enriched_data.tmdb_tv_detail,
            )
    else:
        # No TMDB ID, just convert to enriched seasons without TMDB data
        enriched_seasons = await series_enrichment_service.build_enriched_seasons(
            series_detail=enriched_data.series_detail,
            tmdb_id=None,
            tmdb_tv_detail=None,
        )

    return SeasonsResponse(
        content_type=provider.content_type,
        seasons=enriched_seasons,
        # New structure
        tmdb_series_data=enriched_data.tmdb_tv_detail,
        match_confidence=enriched_data.match_confidence,
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
    for that season only, with embedded tmdb_episode_data for each episode.
    """
    enriched_data = await fetch_series_with_enrichment(
        source=source,
        url=url,
        fetch_episodes=True,
    )

    # Find the requested season
    season = series_enrichment_service.find_season(
        enriched_data.series_detail, season_num
    )

    if not season:
        raise HTTPException(
            status_code=404, detail=f"Season {season_num} not found"
        )

    provider = get_provider(source)

    # Enrich with TMDB season data if we have TMDB ID
    if enriched_data.tmdb_id:
        try:
            async with tmdb_service:
                enriched_season, tmdb_season = (
                    await series_enrichment_service.enrich_season_with_tmdb(
                        season=season,
                        tmdb_id=enriched_data.tmdb_id,
                        season_number=season_num,
                    )
                )
        except (httpx.HTTPError, ValueError, RuntimeError):
            logger.exception(
                "Failed to enrich season with TMDB data, using provider data only"
            )
            enriched_season = (
                SeriesEnrichmentService.convert_season_to_enriched(season)
            )
    else:
        enriched_season = SeriesEnrichmentService.convert_season_to_enriched(season)

    return SeasonResponse(
        content_type=provider.content_type,
        season=enriched_season,
        # New structure
        tmdb_series_data=enriched_data.tmdb_tv_detail,
        match_confidence=enriched_data.match_confidence,
    )


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
    enriched_data = await fetch_series_with_enrichment(
        source=source,
        url=url,
        fetch_episodes=True,
    )

    # Find the requested season
    season = series_enrichment_service.find_season(
        enriched_data.series_detail, season_num
    )

    if not season:
        raise HTTPException(
            status_code=404, detail=f"Season {season_num} not found"
        )

    # Find the requested episode
    episode = series_enrichment_service.find_episode(season, episode_num)

    if not episode:
        raise HTTPException(
            status_code=404,
            detail=f"Episode {episode_num} not found in season {season_num}",
        )

    provider = get_provider(source)

    # Fetch TMDB episode details with full data (crew, guest_stars, videos, images)
    if enriched_data.tmdb_id:
        try:
            async with tmdb_service:
                enriched_episode = (
                    await series_enrichment_service.get_enriched_episode(
                        episode=episode,
                        tmdb_id=enriched_data.tmdb_id,
                        season_number=season_num,
                        episode_number=episode_num,
                    )
                )
        except (httpx.HTTPError, ValueError, RuntimeError):
            logger.exception(
                "Failed to fetch TMDB episode data, using provider data only"
            )
            enriched_episode = (
                SeriesEnrichmentService.convert_episode_to_enriched(episode)
            )
    else:
        enriched_episode = SeriesEnrichmentService.convert_episode_to_enriched(episode)

    return EpisodeResponse(
        content_type=provider.content_type,
        episode=enriched_episode,
        # New structure
        tmdb_series_data=enriched_data.tmdb_tv_detail,
        match_confidence=enriched_data.match_confidence,
    )


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
    enriched_data = await fetch_series_with_enrichment(
        source=source,
        url=url,
        fetch_episodes=True,
    )

    provider = get_provider(source)

    return MoviesResponse(
        content_type=provider.content_type,
        movies=enriched_data.series_detail.movies,
        # New structure
        tmdb_series_data=enriched_data.tmdb_tv_detail,
        match_confidence=enriched_data.match_confidence,
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
    enriched_data = await fetch_series_with_enrichment(
        source=source,
        url=url,
        fetch_episodes=True,
    )

    # Find the requested movie
    movie = None
    for m in enriched_data.series_detail.movies:
        if m.number == movie_num:
            movie = m
            break

    if not movie:
        raise HTTPException(
            status_code=404, detail=f"Movie {movie_num} not found"
        )

    provider = get_provider(source)

    return MovieResponse(
        content_type=provider.content_type,
        movie=movie,
        # New structure
        tmdb_series_data=enriched_data.tmdb_tv_detail,
        match_confidence=enriched_data.match_confidence,
    )
