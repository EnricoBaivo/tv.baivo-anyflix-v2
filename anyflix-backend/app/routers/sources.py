"""Media sources API router."""

import logging
import os
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from lib.extractors.ytdlp_extractor import ytdlp_extractor
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
    TrailerRequest,
    TrailerResponse,
    VideoListResponse,
)
from lib.providers.aniworld import AniWorldProvider
from lib.providers.base import BaseProvider
from lib.providers.serienstream import SerienStreamProvider
from lib.services.anilist_service import AniListService
from lib.services.tmdb_service import TMDBService
from lib.utils.external_data_converters import (
    safe_convert_anilist_data,
    safe_convert_tmdb_data,
)
from lib.utils.trailer_utils import extract_trailer_info

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
                        # Take the first result and convert to structured data
                        first_result = anilist_data.media[0]
                        raw_data = (
                            first_result.model_dump()
                            if hasattr(first_result, "model_dump")
                            else first_result.dict()
                        )
                        result.anilist_data = safe_convert_anilist_data(raw_data)
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
                        result.tmdb_data = safe_convert_tmdb_data(tmdb_data)
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
        "match_confidence": None,
    }

    if provider.type == "anime":
        try:
            async with anilist_service:
                anilist_data = await anilist_service.search_anime(
                    detail_response.media.name
                )
                if (
                    anilist_data
                    and hasattr(anilist_data, "media")
                    and anilist_data.media
                ):
                    # Take the first result and convert to structured data
                    first_result = anilist_data.media[0]
                    raw_data = (
                        first_result.model_dump()
                        if hasattr(first_result, "model_dump")
                        else first_result.dict()
                    )
                    response_data["anilist_data"] = safe_convert_anilist_data(raw_data)
                    response_data["match_confidence"] = 1.0
        except Exception as e:
            logger.warning(f"Failed to enrich with AniList data for series: {e}")
            pass
    elif provider.type == "normal":
        if tmdb_service._api_available:
            try:
                async with tmdb_service:
                    tmdb_data = await tmdb_service.search_and_match(
                        detail_response.media.name, media_type="tv"
                    )
                    if tmdb_data:
                        response_data["tmdb_data"] = safe_convert_tmdb_data(tmdb_data)
                        response_data["match_confidence"] = 1.0
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
    return SeasonsResponse(
        type=series_detail.type,
        seasons=series_detail.series.seasons,
        tmdb_data=series_detail.tmdb_data,
        anilist_data=series_detail.anilist_data,
        match_confidence=getattr(series_detail, "match_confidence", None),
    )


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
    return MoviesResponse(
        type=series_detail.type,
        movies=series_detail.series.movies,
        tmdb_data=series_detail.tmdb_data,
        anilist_data=series_detail.anilist_data,
        match_confidence=getattr(series_detail, "match_confidence", None),
    )


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
            return MovieResponse(
                type=series_detail.type,
                movie=movie,
                tmdb_data=series_detail.tmdb_data,
                anilist_data=series_detail.anilist_data,
                match_confidence=getattr(series_detail, "match_confidence", None),
            )

    raise HTTPException(status_code=404, detail=f"Movie {movie_num} not found")


@router.post(
    "/trailer",
    response_model=TrailerResponse,
    summary="🎬 Extract Streamable Trailer URL",
)
async def extract_trailer_url(request: TrailerRequest):
    """
    Extract streamable URL from AniList or TMDB trailer data.

    Takes trailer information from AniList or TMDB responses, builds the full YouTube URL,
    and uses ytdlp_extractor to get the actual streamable URL.

    Args:
        request: TrailerRequest containing either anilist_trailer or tmdb_trailer data

    Returns:
        TrailerResponse with streamable URL and metadata
    """
    try:
        youtube_url = None
        site = None
        source_type = None

        # Process AniList trailer data
        if request.anilist_trailer:
            youtube_url, site = extract_trailer_info(request.anilist_trailer, "anilist")
            source_type = "anilist"
            logger.info(f"Processing AniList trailer: {request.anilist_trailer}")

        # Process TMDB trailer data
        elif request.tmdb_trailer:
            youtube_url, site = extract_trailer_info(request.tmdb_trailer, "tmdb")
            source_type = "tmdb"
            logger.info(f"Processing TMDB trailer: {request.tmdb_trailer}")

        else:
            return TrailerResponse(
                success=False,
                original_url="",
                error="No trailer data provided. Please provide either anilist_trailer or tmdb_trailer.",
            )

        if not youtube_url:
            return TrailerResponse(
                success=False,
                original_url="",
                error=f"Unable to build YouTube URL from {source_type} trailer data",
            )

        logger.info(f"Built YouTube URL: {youtube_url}")

        # Use ytdlp_extractor to get streamable URL
        try:
            video_sources = await ytdlp_extractor(youtube_url)

            if not video_sources:
                return TrailerResponse(
                    success=False,
                    original_url=youtube_url,
                    site=site,
                    error="No streamable URLs found for this trailer",
                )

            # Get the best quality source (first one from ytdlp - now sorted by quality)
            best_source = video_sources[0]

            return TrailerResponse(
                success=True,
                original_url=youtube_url,
                streamable_url=best_source.url,
                quality=best_source.quality,
                site=site,
            )

        except Exception as extraction_error:
            logger.error(
                f"ytdlp extraction failed for {youtube_url}: {extraction_error}"
            )
            return TrailerResponse(
                success=False,
                original_url=youtube_url,
                site=site,
                error=f"Failed to extract streamable URL: {str(extraction_error)}",
            )

    except Exception as e:
        logger.error(f"Trailer extraction error: {e}")
        return TrailerResponse(
            success=False, original_url="", error=f"Internal error: {str(e)}"
        )
