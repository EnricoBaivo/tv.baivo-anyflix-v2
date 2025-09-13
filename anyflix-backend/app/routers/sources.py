"""Media sources API router."""

import logging
import os
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from lib.models.base import SearchResult
from lib.models.responses import (
    EpisodeResponse,
    LatestResponse,
    MovieResponse,
    MoviesResponse,
    PopularResponse,
    SearchResponse,
    SeasonResponse,
    SeasonsResponse,
    SeriesDetailResponse,
    VideoListResponse,
)
from lib.providers.aniworld import AniWorldProvider
from lib.providers.base import BaseProvider
from lib.providers.serienstream import SerienStreamProvider
from lib.services.anilist_service import AniListService
from lib.services.tmdb_service import TMDBService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sources",
    tags=["media-api"],
    responses={
        404: {"description": "Source not found"},
        500: {"description": "Internal server error"},
    },
)

# Initialize providers with proper typing
providers: Dict[str, BaseProvider] = {
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


async def enrich_with_metadata(
    results: List[SearchResult], type: str
) -> List[SearchResult]:
    """Enrich results with metadata based on source type.

    Args:
        results: List of SearchResult objects to enrich
        source: Source name ('aniworld' or 'serienstream')

    Returns:
        List[SearchResult]: The enriched results
    """
    for result in results:
        if type == "anime":
            # Add AniList metadata for anime
            try:
                async with anilist_service:
                    anilist_data = await anilist_service.search_anime(result.name)
                    if (
                        anilist_data
                        and hasattr(anilist_data, "media")
                        and anilist_data.media
                    ):
                        # Take the first result and convert to dict
                        first_result = anilist_data.media[0]
                        result.anilist_data = (
                            first_result.model_dump()
                            if hasattr(first_result, "model_dump")
                            else first_result.dict()
                        )
                        result.match_confidence = 1.0
                    else:
                        result.anilist_data = None
            except Exception as e:
                logger.warning(f"Failed to enrich with AniList data: {e}")
                result.anilist_data = None
        elif type == "normal":
            # Add TMDB metadata for series (only if API key is available)
            if tmdb_service._api_available:
                try:
                    async with tmdb_service:
                        tmdb_data = await tmdb_service.search_and_match(
                            result.name, media_type="tv"
                        )
                        result.tmdb_data = tmdb_data
                        if tmdb_data:
                            result.match_confidence = 1.0
                        else:
                            result.tmdb_data = None
                except Exception as e:
                    logger.warning(f"Failed to enrich with TMDB data: {e}")
                    result.tmdb_data = None
            else:
                result.tmdb_data = None
    return results


@router.get("/", summary="📋 List Available Sources")
async def get_sources():
    """Get all available media sources."""
    return {"sources": list(providers.keys())}


@router.get("/{source}/preferences", summary="📋 Get Source Configuration")
async def get_source_preferences(source: str = Path(...)):
    """Get configuration preferences for a specific source."""
    provider = get_provider(source)
    async with provider:
        preferences = provider.get_source_preferences()
        return {"preferences": preferences}


@router.get(
    "/{source}/popular",
    response_model=PopularResponse,
    summary="🔍 Get Popular Content",
)
async def get_popular(
    source: str = Path(...),
    page: int = Query(1, ge=1),
):
    """Get popular content with optional metadata enrichment."""
    provider = get_provider(source)
    async with provider:
        result = await provider.get_popular(page)
        result.list = await enrich_with_metadata(result.list, provider.type)
        return result


@router.get(
    "/{source}/latest", response_model=LatestResponse, summary="🔍 Get Latest Updates"
)
async def get_latest_updates(
    source: str = Path(...),
    page: int = Query(1, ge=1),
):
    """Get latest updates with optional metadata enrichment."""
    provider = get_provider(source)
    async with provider:
        result = await provider.get_latest_updates(page)
        result.list = await enrich_with_metadata(result.list, provider.type)
        return result


@router.get(
    "/{source}/search", response_model=SearchResponse, summary="🔍 Search Content"
)
async def search_content(
    source: str = Path(...),
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    lang: str = Query(None),
):
    """Search for content with optional metadata enrichment."""
    provider = get_provider(source)
    async with provider:
        result = await provider.search(q, page, lang)
        result.list = await enrich_with_metadata(result.list, provider.type)
        return result


@router.get(
    "/{source}/videos",
    response_model=VideoListResponse,
    summary="🎬 Get Video Streaming Links",
)
async def get_video_sources(
    source: str = Path(...),
    url: str = Query(...),
    lang: str = Query(None),
):
    """Get video sources."""
    provider = get_provider(source)
    async with provider:
        return await provider.get_video_list(url, lang)


@router.get(
    "/{source}/series",
    response_model=SeriesDetailResponse,
    summary="📺 Get Full Series Data",
)
async def get_series_detail(
    source: str = Path(...),
    url: str = Query(...),
):
    """Get complete series data with hierarchical structure."""
    provider = get_provider(source)

    # Get flat detail response
    async with provider:
        detail_response = await provider.get_detail(url)

    # Convert to hierarchical structure (simplified)
    from lib.models.base import Movie, MovieKind, Season, SeriesDetail

    slug = url.split("/")[-1] if "/" in url else "unknown"

    # Simple conversion - group episodes by season
    seasons_dict = {}
    movies = []

    for ep_data in detail_response.media.episodes:
        if isinstance(ep_data, dict):
            # Check if this is a movie/film
            if ep_data.get("kind") == "movie" or "/filme/" in ep_data.get("url", ""):
                movies.append(
                    Movie(
                        number=ep_data.get("number", 1),
                        title=ep_data.get("title", ""),
                        kind=MovieKind.MOVIE,  # Default to movie for films
                        url=ep_data.get("url", ""),
                        date_upload=ep_data.get("date_upload"),
                        tags=ep_data.get("tags", []),
                    )
                )
            else:
                # Handle regular episodes
                season_num = ep_data.get("season", 1)
                episode_num = ep_data.get("episode", 1)

                if season_num not in seasons_dict:
                    seasons_dict[season_num] = Season(
                        season=season_num, title=f"Staffel {season_num}", episodes=[]
                    )

                from lib.models.base import Episode

                seasons_dict[season_num].episodes.append(
                    Episode(
                        season=season_num,
                        episode=episode_num,
                        title=ep_data.get("title", ""),
                        url=ep_data.get("url", ""),
                        date_upload=ep_data.get("date_upload"),
                        tags=ep_data.get("tags", []),
                    )
                )

    # Sort seasons and episodes
    seasons = sorted(seasons_dict.values(), key=lambda s: s.season)
    for season in seasons:
        season.episodes.sort(key=lambda e: e.episode)

    series_detail = SeriesDetail(slug=slug, seasons=seasons, movies=movies)

    # Add metadata based on source
    response_data = {
        "type": provider.type,
        "length": len(detail_response.media.episodes),
        "series": series_detail,
        "tmdb_data": None,
        "anilist_data": None,
    }

    if provider.type == "anime":
        try:
            async with anilist_service:
                anilist_data = await anilist_service.search_anime(detail_response)
                if anilist_data and anilist_data.get("data"):
                    response_data["anilist_data"] = anilist_data["data"]
        except Exception:
            pass
    elif provider.type == "normal":
        if tmdb_service._api_available:
            try:
                async with tmdb_service:
                    tmdb_data = await tmdb_service.search_and_match(
                        detail_response.media.name, media_type="tv"
                    )
                    response_data["tmdb_data"] = tmdb_data
            except Exception as e:
                logger.warning(f"Failed to get TMDB data for series: {e}")
        else:
            logger.info("TMDB API key not configured, skipping metadata enrichment")

    return SeriesDetailResponse(**response_data)


@router.get(
    "/{source}/series/seasons",
    response_model=SeasonsResponse,
    summary="📺 Get All Seasons",
)
async def get_series_seasons(
    source: str = Path(...),
    url: str = Query(...),
):
    """Get all seasons for a series."""
    series_detail = await get_series_detail(source, url)
    return SeasonsResponse(seasons=series_detail.series.seasons)


@router.get(
    "/{source}/series/seasons/{season_num}",
    response_model=SeasonResponse,
    summary="📺 Get Specific Season",
)
async def get_series_season(
    source: str = Path(...),
    season_num: int = Path(..., ge=1),
    url: str = Query(...),
):
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
    summary="📺 Get Specific Episode",
)
async def get_series_episode(
    source: str = Path(...),
    season_num: int = Path(..., ge=1),
    episode_num: int = Path(..., ge=1),
    url: str = Query(...),
):
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
    summary="📺 Get All Movies/OVAs",
)
async def get_series_movies(
    source: str = Path(...),
    url: str = Query(...),
):
    """Get all movies, OVAs, and specials for a series."""
    series_detail = await get_series_detail(source, url)
    return MoviesResponse(movies=series_detail.series.movies)


@router.get(
    "/{source}/series/movies/{movie_num}",
    response_model=MovieResponse,
    summary="📺 Get Specific Movie/OVA",
)
async def get_series_movie(
    source: str = Path(...),
    movie_num: int = Path(..., ge=1),
    url: str = Query(...),
):
    """Get details for a specific movie, OVA, or special."""
    series_detail = await get_series_detail(source, url)

    for movie in series_detail.series.movies:
        if movie.number == movie_num:
            return MovieResponse(movie=movie)

    raise HTTPException(status_code=404, detail=f"Movie {movie_num} not found")
