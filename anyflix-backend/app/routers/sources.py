"""Media sources API router."""

import logging
import os

import httpx
from fastapi import APIRouter, HTTPException, Path, Query

from lib.extractors.ytdlp_extractor import ytdlp_extractor
from lib.models.responses import (
    LatestResponse,
    PopularResponse,
    PreferencesResponse,
    SearchResponse,
    SourcesResponse,
    TrailerRequest,
    TrailerResponse,
    VideoListResponse,
)
from lib.providers.aniworld import AniWorldProvider
from lib.providers.base import BaseProvider
from lib.providers.serienstream import SerienStreamProvider
from lib.services.anilist_service import AniListService
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


@router.get("/", response_model=SourcesResponse, summary="📋 List Available Sources")
async def get_sources() -> SourcesResponse:
    """Get all available media sources."""
    return SourcesResponse(sources=list(providers.keys()))


@router.get(
    "/{source}/preferences",
    response_model=PreferencesResponse,
    summary="📋 Get Source Configuration",
)
async def get_source_preferences(source: str = Path(...)) -> PreferencesResponse:
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
) -> PopularResponse:
    """Get popular content with optional metadata enrichment."""
    provider = get_provider(source)
    async with provider:
        return await provider.get_popular(page)


@router.get(
    "/{source}/latest", response_model=LatestResponse, summary="🔍 Get Latest Updates"
)
async def get_latest_updates(
    source: str = Path(...),
    page: int = Query(1, ge=1),
) -> LatestResponse:
    """Get latest updates with optional metadata enrichment."""
    provider = get_provider(source)
    async with provider:
        return await provider.get_latest_updates(page)


@router.get(
    "/{source}/search", response_model=SearchResponse, summary="🔍 Search Content"
)
async def search_content(
    source: str = Path(...),
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    lang: str = Query(None),
) -> SearchResponse:
    """Search for content with optional metadata enrichment."""
    provider = get_provider(source)
    async with provider:
        return await provider.search(q, page, lang)


@router.get(
    "/{source}/videos",
    response_model=VideoListResponse,
    summary="🎬 Get Video Streaming Links",
)
async def get_video_sources(
    source: str = Path(...),
    url: str = Query(...),
    lang: str = Query(None),
) -> VideoListResponse:
    """Get video sources."""
    provider = get_provider(source)
    async with provider:
        return await provider.get_video_list(url, lang)


@router.post(
    "/trailer",
    response_model=TrailerResponse,
    summary="🎬 Extract Streamable Trailer URL",
)
async def extract_trailer_url(request: TrailerRequest) -> TrailerResponse:
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
            logger.info("Processing AniList trailer: %s", request.anilist_trailer)

        # Process TMDB trailer data
        elif request.tmdb_trailer:
            youtube_url, site = extract_trailer_info(request.tmdb_trailer, "tmdb")
            source_type = "tmdb"
            logger.info("Processing TMDB trailer: %s", request.tmdb_trailer)

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

        logger.info("Built YouTube URL: %s", youtube_url)

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
            logger.exception("ytdlp extraction failed for %s", youtube_url)
            return TrailerResponse(
                success=False,
                original_url=youtube_url,
                site=site,
                error=f"Failed to extract streamable URL: {extraction_error!s}",
            )

    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        logger.exception("Trailer extraction error")
        return TrailerResponse(
            success=False, original_url="", error=f"Internal error: {e!s}"
        )
