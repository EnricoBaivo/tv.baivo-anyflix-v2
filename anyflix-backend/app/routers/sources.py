"""Media sources API router."""

import logging
import os
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, HTTPException, Path, Query

from lib.extractors.ytdlp_extractor import ytdlp_extractor
from lib.models.anilist import Media
from lib.models.base import SearchResult
from lib.models.responses import (
    EpisodeResponse,
    LatestResponse,
    MovieResponse,
    MoviesResponse,
    PopularResponse,
    PreferencesResponse,
    SearchResponse,
    SeasonResponse,
    SeasonsResponse,
    SeriesDetailResponse,
    SourcesResponse,
    TrailerRequest,
    TrailerResponse,
    VideoListResponse,
)
from lib.models.tmdb import TMDBMovieDetail, TMDBTVDetail
from lib.providers.aniworld import AniWorldProvider
from lib.providers.base import BaseProvider
from lib.providers.serienstream import SerienStreamProvider
from lib.services.anilist_service import AniListService
from lib.services.matching_service import MatchingService
from lib.services.series_converter import SeriesConverterService
from lib.services.tmdb_service import TMDBService
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


async def enrich_single_item_metadata(
    title: str, source_type: str
) -> tuple[
    Optional[Union[TMDBMovieDetail, TMDBTVDetail]], Optional[Media], Optional[float]
]:
    """Enrich a single item with metadata based on source type.

    Args:
        title: Title to search for
        source_type: Source type ('anime' or 'normal')

    Returns:
        Tuple of (tmdb_data, anilist_data, match_confidence)
    """
    tmdb_data = None
    anilist_data = None
    match_confidence = None

    if source_type == "anime":
        # Add AniList metadata for anime
        try:
            async with anilist_service:
                anilist_search_result = await anilist_service.search_anime(title)
                anilist_data, match_confidence = (
                    MatchingService.find_best_anilist_match(
                        title, anilist_search_result
                    )
                )
        except Exception as e:
            logger.warning(f"Failed to enrich with AniList data: {e}")
    elif source_type == "normal":
        # Add TMDB metadata for series (only if API key is available)
        if tmdb_service._api_available:
            try:
                async with tmdb_service:
                    tmdb_data = await tmdb_service.search_and_match(
                        title, media_type="tv"
                    )
                    match_confidence = (
                        MatchingService.calculate_tmdb_confidence(title, tmdb_data)
                        if tmdb_data
                        else None
                    )
            except Exception as e:
                logger.warning(f"Failed to enrich with TMDB data: {e}")
        else:
            logger.info("TMDB API key not configured, skipping metadata enrichment")

    return tmdb_data, anilist_data, match_confidence


async def enrich_with_metadata(
    results: List[SearchResult], source_type: str
) -> List[SearchResult]:
    """Enrich results with metadata based on source type.

    Args:
        results: List of SearchResult objects to enrich
        source_type: Source type ('anime' or 'normal')

    Returns:
        List[SearchResult]: The enriched results
    """
    for result in results:
        tmdb_data, anilist_data, match_confidence = await enrich_single_item_metadata(
            result.name, source_type
        )
        result.tmdb_data = tmdb_data
        result.anilist_data = anilist_data
        result.match_confidence = match_confidence
    return results


@router.get("/", response_model=SourcesResponse, summary="📋 List Available Sources")
async def get_sources():
    """Get all available media sources."""
    return SourcesResponse(sources=list(providers.keys()))


@router.get(
    "/{source}/preferences",
    response_model=PreferencesResponse,
    summary="📋 Get Source Configuration",
)
async def get_source_preferences(source: str = Path(...)):
    """Get configuration preferences for a specific source."""
    provider = get_provider(source)
    async with provider:
        preferences_list = provider.get_source_preferences()
        # Convert list of SourcePreference to dict format expected by response
        preferences_dict = {pref.key: pref.model_dump() for pref in preferences_list}
        return PreferencesResponse(preferences=preferences_dict)


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
        # Guard against cache deserialization issues
        if not hasattr(result, "list") or not hasattr(result, "type"):
            logger.error(f"Invalid result from get_popular: {type(result)} - {result}")
            raise HTTPException(
                status_code=500, detail="Provider returned invalid response format"
            )
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
        # Guard against cache deserialization issues
        if not hasattr(result, "list") or not hasattr(result, "type"):
            logger.error(
                f"Invalid result from get_latest_updates: {type(result)} - {result}"
            )
            raise HTTPException(
                status_code=500, detail="Provider returned invalid response format"
            )
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
    try:
        async with provider:
            detail_response = await provider.get_detail(url)
            # Guard against cache deserialization issues
            if not hasattr(detail_response, "media"):
                logger.error(
                    f"Invalid detail response from provider {source}: {type(detail_response)} - {detail_response}"
                )
                raise HTTPException(
                    status_code=500, detail="Provider returned invalid response format"
                )
    except Exception as e:
        logger.error(f"Failed to get detail from provider {source}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch series data from {source}"
        )

    # Convert to hierarchical structure using converter service
    try:
        slug = url.split("/")[-1] if "/" in url else "unknown"
        series_detail = SeriesConverterService.convert_to_hierarchical(
            detail_response, slug=slug
        )
    except ValueError as e:
        logger.error(f"Failed to convert series to hierarchical structure: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process series data structure"
        )

    # Add metadata based on source type
    tmdb_data, anilist_data, match_confidence = await enrich_single_item_metadata(
        detail_response.media.name, provider.type
    )

    return SeriesDetailResponse(
        type=provider.type,
        series=series_detail,
        length=len(detail_response.media.episodes),
        tmdb_data=tmdb_data,
        anilist_data=anilist_data,
        match_confidence=match_confidence,
    )


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
        match_confidence=series_detail.match_confidence,
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
        match_confidence=series_detail.match_confidence,
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
                match_confidence=series_detail.match_confidence,
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
