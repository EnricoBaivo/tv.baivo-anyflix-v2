"""Media sources API router."""

import logging

from fastapi import APIRouter, Path, Query

from app.providers import get_provider, providers
from lib.extractors.ytdlp_extractor import ytdlp_extractor
from lib.models.responses import (
    PaginatedSearchResultResponse,
    PreferencesResponse,
    SourcesResponse,
    TrailerResponse,
    VideoListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sources",
    tags=["media-api"],
    responses={
        404: {"description": "Source not found"},
        500: {"description": "Internal server error"},
    },
)


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
    response_model=PaginatedSearchResultResponse,
    summary="🔍 Get Popular Content",
)
async def get_popular(
    source: str = Path(...),
    page: int = Query(1, ge=1),
) -> PaginatedSearchResultResponse:
    """Get popular content."""
    provider = get_provider(source)
    async with provider:
        return await provider.get_popular(page=page)


@router.get(
    "/{source}/latest",
    response_model=PaginatedSearchResultResponse,
    summary="🔍 Get Latest Updates",
)
async def get_latest_updates(
    source: str = Path(...),
    page: int = Query(1, ge=1),
) -> PaginatedSearchResultResponse:
    """Get latest updates."""
    provider = get_provider(source)
    async with provider:
        return await provider.get_latest_updates(page=page)


@router.get(
    "/{source}/search",
    response_model=PaginatedSearchResultResponse,
    summary="🔍 Search Content",
)
async def search_content(
    source: str = Path(...),
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    lang: str = Query(None),
) -> PaginatedSearchResultResponse:
    """Search for content."""
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
        logger.debug(
            "Getting video list for %s with language filter %s (source: %s)",
            url,
            lang,
            source,
        )
        return await provider.get_video_list(url, lang)


@router.get(
    "/trailer",
    response_model=TrailerResponse,
    summary="🎬 Extract Streamable Trailer URL",
)
async def extract_trailer_url(youtube_url: str) -> TrailerResponse:
    """
    Extract streamable URL from AniList or TMDB trailer data.

    Takes trailer information from AniList or TMDB responses, builds the full YouTube URL,
    and uses ytdlp_extractor to get the actual streamable URL.

    Args:
        request: TrailerRequest containing either anilist_trailer or tmdb_trailer data

    Returns:
        TrailerResponse with streamable URL and metadata
    """
    if not youtube_url.startswith("https://www.youtube.com/watch?v="):
        return TrailerResponse(
            success=False,
            original_url=youtube_url,
            error="Invalid YouTube URL",
        )
    # Use ytdlp_extractor to get streamable URL
    try:
        video_sources = await ytdlp_extractor(youtube_url)

        if not video_sources:
            return TrailerResponse(
                success=False,
                original_url=youtube_url,
                error="No streamable URLs found for this trailer",
            )

        best_source = video_sources[0]
        # find m3u8 url with best quality
        m3u8_url = next(
            (source.url for source in video_sources if source.format == "m3u8"), None
        )
        # find combined url with best quality
        combined_url = next(
            (source.url for source in video_sources if source.format == "combined"),
            None,
        )
        return TrailerResponse(
            success=True,
            original_url=youtube_url,
            streamable_url=combined_url,
            m3u8_url=m3u8_url,
            quality=best_source.quality,
        )

    except Exception as extraction_error:
        logger.exception("ytdlp extraction failed for %s", youtube_url)
        return TrailerResponse(
            success=False,
            original_url=youtube_url,
            error=f"Failed to extract streamable URL: {extraction_error!s}",
        )
