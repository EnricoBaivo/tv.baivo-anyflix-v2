"""Anime sources API router with comprehensive OpenAPI documentation."""

from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from lib.models.enhanced import (
    EnhancedLatestResponse,
    EnhancedPopularResponse,
    EnhancedSearchResponse,
    EnhancedSeriesDetailResponse,
    EnhancedVideoListResponse,
)
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
from lib.services.media_service import MediaService

from ..dependencies import get_anime_service, get_enhanced_anime_service

router = APIRouter(
    prefix="/sources",
    tags=["media-api"],
    responses={
        404: {"description": "Source not found"},
        500: {"description": "Internal server error"},
    },
)


@router.get(
    "/",
    summary="📋 List Available Sources",
    description="**Source Management**: Retrieve a list of all available streaming sources for media content.",
    response_description="List of available streaming sources",
    operation_id="list_sources",
    responses={
        200: {
            "description": "Successfully retrieved sources",
            "content": {
                "application/json": {
                    "example": {"sources": ["aniworld", "serienstream"]}
                }
            },
        }
    },
)
async def get_sources(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get all available anime sources with metadata capabilities.

    Returns a list of source identifiers that can be used with other endpoints
    to access anime content from different streaming platforms, with optional
    AniList metadata enrichment support.
    """
    return {
        "sources": enhanced_service.get_available_sources(),
        "metadata_support": enhanced_service.enable_metadata,
        "features": [
            "Basic streaming source data",
            "Optional AniList metadata enrichment",
            "Professional caching system",
            "Anime-only filtering",
        ],
    }


@router.get(
    "/{source}/preferences",
    summary="📋 Get Source Configuration",
    description="**Source Management**: Retrieve configuration preferences for a specific streaming source including language, quality, and host settings.",
    response_description="Source preferences configuration",
    operation_id="get_source_preferences",
    responses={
        200: {
            "description": "Successfully retrieved preferences",
            "content": {
                "application/json": {
                    "example": {
                        "preferences": [
                            {
                                "key": "lang",
                                "list_preference": {
                                    "title": "Bevorzugte Sprache",
                                    "entries": ["Deutsch", "Englisch"],
                                    "entryValues": ["Deutscher", "Englischer"],
                                },
                            }
                        ]
                    }
                }
            },
        }
    },
)
async def get_source_preferences(
    source: str = Path(
        ..., description="Source identifier (e.g., 'aniworld', 'serienstream')"
    ),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get configuration preferences for a specific anime source.

    Preferences control playback settings like language, quality, and host preferences.
    """
    try:
        preferences = enhanced_service.get_source_preferences(source)
        return {"preferences": preferences}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{source}/popular",
    response_model=Union[PopularResponse, EnhancedPopularResponse],
    summary="🔍 Get Popular Content",
    description="**Content Discovery**: Retrieve popular anime with optional AniList metadata enrichment including ratings, genres, characters, and more. AniWorld responses automatically include metadata.",
    response_description="List of popular content with optional metadata",
    operation_id="get_popular_content",
    responses={
        200: {
            "description": "Successfully retrieved popular anime",
            "content": {
                "application/json": {
                    "examples": {
                        "basic": {
                            "summary": "Basic response (include_metadata=false)",
                            "value": {
                                "list": [
                                    {
                                        "name": "Attack on Titan",
                                        "image_url": "https://example.com/image.jpg",
                                        "link": "/anime/stream/attack-on-titan",
                                    }
                                ],
                                "has_next_page": False,
                            },
                        },
                        "enhanced": {
                            "summary": "Enhanced response (include_metadata=true)",
                            "value": {
                                "list": [
                                    {
                                        "name": "Attack on Titan",
                                        "image_url": "https://example.com/image.jpg",
                                        "link": "/anime/stream/attack-on-titan",
                                        "anilist_id": 16498,
                                        "match_confidence": 0.95,
                                        "anilist_data": {
                                            "averageScore": 84,
                                            "genres": ["Action", "Drama", "Fantasy"],
                                            "trailer": {
                                                "site": "youtube",
                                                "id": "abc123",
                                            },
                                        },
                                    }
                                ],
                                "has_next_page": False,
                                "metadata_coverage": 85.5,
                            },
                        },
                    }
                }
            },
        }
    },
)
async def get_popular(
    source: str = Path(..., description="Source identifier"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    include_metadata: bool = Query(
        False,
        description="Include AniList metadata enrichment (scores, genres, trailers, etc.)",
    ),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get popular anime with optional AniList metadata enrichment.

    Returns a paginated list of anime sorted by popularity. When `include_metadata=true`,
    results are enriched with comprehensive AniList data including ratings, genres,
    character information, trailers, and more.

    **AniWorld sources automatically include metadata regardless of the parameter.**

    **Enhanced Features** (when include_metadata=true):
    - AniList ratings and popularity scores
    - Complete genre classifications
    - Character and staff information
    - YouTube trailers
    - Related anime recommendations
    - Metadata coverage statistics
    """
    try:
        # Auto-enable metadata for AniWorld sources
        if source.lower() == "aniworld":
            include_metadata = True
        async with enhanced_service:
            return await enhanced_service.get_popular(source, page, include_metadata)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


@router.get(
    "/{source}/latest",
    response_model=Union[LatestResponse, EnhancedLatestResponse],
    summary="🔍 Get Latest Updates",
    description="**Content Discovery**: Retrieve latest anime updates with optional AniList metadata enrichment. AniWorld responses automatically include metadata.",
    response_description="List of recently updated content with optional metadata",
    operation_id="get_latest_updates",
)
async def get_latest_updates(
    source: str = Path(..., description="Source identifier"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    include_metadata: bool = Query(
        False, description="Include AniList metadata enrichment"
    ),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get latest anime updates with optional AniList metadata enrichment.

    Returns recently updated anime with new episodes or content. When metadata
    is enabled, includes comprehensive AniList information.
    """
    try:
        # Auto-enable metadata for AniWorld sources
        if source.lower() == "aniworld":
            include_metadata = True
        async with enhanced_service:
            return await enhanced_service.get_latest_updates(
                source, page, include_metadata
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


@router.get(
    "/{source}/search",
    response_model=Union[SearchResponse, EnhancedSearchResponse],
    summary="🔍 Search Content",
    description="**Content Discovery**: Search for anime with optional AniList metadata enrichment including ratings, trailers, and comprehensive details. AniWorld responses automatically include metadata.",
    response_description="List of content matching the search query with optional metadata",
    operation_id="search_content",
)
async def search_content(
    source: str = Path(..., description="Source identifier"),
    q: str = Query(..., description="Search query (content title)", min_length=1),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    lang: str = Query(None, description="Language filter (de, en, sub, all)"),
    include_metadata: bool = Query(
        False,
        description="Include AniList metadata enrichment (ratings, genres, trailers, etc.)",
    ),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Search for anime with optional AniList metadata enrichment.

    Performs a text search across anime titles and returns matching results.
    When metadata is enabled, includes comprehensive AniList information
    with intelligent title matching and confidence scoring.

    **Enhanced Features** (when include_metadata=true):
    - Smart title matching with confidence scores
    - AniList ratings and popularity
    - Genre classifications and tags
    - YouTube trailers and promotional content
    - Character and staff information
    - Search result statistics and coverage
    """
    try:
        # Auto-enable metadata for AniWorld sources
        if source.lower() == "aniworld":
            include_metadata = True
        async with enhanced_service:
            return await enhanced_service.search(
                source, q, page, lang, include_metadata
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


@router.get(
    "/{source}/videos",
    response_model=Union[VideoListResponse, EnhancedVideoListResponse],
    summary="🎬 Get Video Streaming Links",
    description="**Video Sources**: Get available video streams with optional anime context information for better user experience. AniWorld responses automatically include context.",
    response_description="List of video sources with optional anime context",
    operation_id="get_video_sources",
)
async def get_video_sources(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Episode URL path"),
    lang: str = Query(
        None, description="Preferred language (e.g., 'Deutscher', 'Englischer')"
    ),
    include_context: bool = Query(
        False, description="Include anime and episode context information"
    ),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get video sources with optional anime context information.

    Returns available video streams from different hosting providers with various
    quality options and language/subtitle configurations. When context is enabled,
    includes anime title and episode information extracted from the URL.
    """
    try:
        # Auto-enable context for AniWorld sources
        if source.lower() == "aniworld":
            include_context = True
        async with enhanced_service:
            return await enhanced_service.get_video_list(
                source, url, lang, include_context
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


# ========== SERIES STRUCTURE ENDPOINTS ==========


@router.get(
    "/{source}/series",
    response_model=Union[SeriesDetailResponse, EnhancedSeriesDetailResponse],
    summary="📺 Get Full Series Data",
    description="**Series Structure**: Get complete anime series with optional AniList metadata including character info, staff details, and related anime. AniWorld responses automatically include metadata.",
    response_description="Hierarchical series structure with optional comprehensive metadata",
    operation_id="get_series_detail",
    responses={
        200: {
            "description": "Successfully retrieved hierarchical series detail",
            "content": {
                "application/json": {
                    "examples": {
                        "basic": {
                            "summary": "Basic series structure (include_metadata=false)",
                            "value": {
                                "series": {
                                    "slug": "attack-on-titan",
                                    "seasons": [
                                        {
                                            "season": 4,
                                            "title": "Staffel 4",
                                            "episodes": [
                                                {
                                                    "season": 4,
                                                    "episode": 30,
                                                    "title": "The Final Chapter Part 2",
                                                    "url": "/anime/stream/attack-on-titan/staffel-4/episode-30",
                                                    "date_upload": None,
                                                    "tags": ["Series Final Episode"],
                                                }
                                            ],
                                        }
                                    ],
                                    "movies": [],
                                }
                            },
                        },
                        "enhanced": {
                            "summary": "Enhanced series with metadata (include_metadata=true)",
                            "value": {
                                "series": {
                                    "slug": "attack-on-titan",
                                    "seasons": [
                                        {
                                            "season": 4,
                                            "title": "Staffel 4",
                                            "episodes": [],
                                        }
                                    ],
                                    "movies": [],
                                    "anilist_id": 16498,
                                    "enhanced_title": "Shingeki no Kyojin",
                                    "score": 84,
                                    "year": 2013,
                                    "status_text": "FINISHED",
                                    "studios": ["Wit Studio"],
                                    "characters": [
                                        {"name": "Eren Jaeger", "role": "MAIN"}
                                    ],
                                }
                            },
                        },
                    }
                }
            },
        }
    },
    tags=["media-api"],
)
async def get_series_detail(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    include_metadata: bool = Query(
        False,
        description="Include AniList metadata (characters, staff, relations, etc.)",
    ),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get anime series with hierarchical episode organization and optional AniList metadata.

    Returns episodes organized by seasons and movies/specials separately, providing
    a better structure for frontend applications. When metadata is enabled, includes
    comprehensive AniList information.

    **Core Features:**
    - Episodes grouped by season number
    - Movies/specials in separate collection
    - Extracted tags from episode names
    - Automatic sorting by season/episode numbers
    - Clean title extraction

    **Enhanced Features** (when include_metadata=true):
    - Complete AniList anime information
    - Character and voice actor details
    - Staff and studio information
    - Related anime and recommendations
    - Comprehensive genre and tag data
    - Ratings and popularity metrics
    """
    try:
        # Auto-enable metadata for AniWorld sources
        if source.lower() == "aniworld":
            include_metadata = True
        async with enhanced_service:
            return await enhanced_service.get_series_detail(
                source, url, include_metadata
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


@router.get(
    "/{source}/series/seasons",
    response_model=SeasonsResponse,
    summary="📺 Get All Seasons",
    description="**Series Structure**: Get list of all seasons for a series with their episodes, sorted by season number. AniWorld responses automatically include AniList metadata.",
    response_description="List of all seasons with their episodes",
    operation_id="get_all_seasons",
    tags=["media-api"],
)
async def get_series_seasons(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get all seasons for a series.

    Returns a complete list of all seasons with their episodes, sorted by season number.
    For AniWorld sources, automatically includes AniList metadata enrichment.
    """
    try:
        # Enable metadata for AniWorld sources
        include_metadata = source.lower() == "aniworld"
        async with enhanced_service:
            series_detail = await enhanced_service.get_series_detail(
                source, url, include_metadata
            )
        return SeasonsResponse(seasons=series_detail.series.seasons)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


@router.get(
    "/{source}/series/seasons/{season_num}",
    response_model=SeasonResponse,
    summary="📺 Get Specific Season",
    description="**Series Structure**: Get details for a specific season including all its episodes, sorted by episode number. AniWorld responses automatically include AniList metadata.",
    response_description="Season details with all episodes",
    operation_id="get_season_detail",
    responses={404: {"description": "Season not found"}},
    tags=["media-api"],
)
async def get_series_season(
    source: str = Path(..., description="Source identifier"),
    season_num: int = Path(..., description="Season number", ge=1),
    url: str = Query(..., description="Anime URL path"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get details for a specific season.

    Returns all episodes for the specified season number, sorted by episode number.
    For AniWorld sources, automatically includes AniList metadata enrichment.
    """
    try:
        # Enable metadata for AniWorld sources
        include_metadata = source.lower() == "aniworld"
        async with enhanced_service:
            series_detail = await enhanced_service.get_series_detail(
                source, url, include_metadata
            )
        for season in series_detail.series.seasons:
            if season.season == season_num:
                return SeasonResponse(season=season)
        raise HTTPException(status_code=404, detail=f"Season {season_num} not found")
    except HTTPException:
        # Re-raise HTTPExceptions (like our 404) without wrapping them
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


@router.get(
    "/{source}/series/seasons/{season_num}/episodes/{episode_num}",
    response_model=EpisodeResponse,
    summary="📺 Get Specific Episode",
    description="**Series Structure**: Get details for a specific episode within a season, including title, URL, tags, and metadata. AniWorld responses automatically include AniList metadata.",
    response_description="Episode details",
    operation_id="get_episode_detail",
    responses={404: {"description": "Season or episode not found"}},
    tags=["media-api"],
)
async def get_series_episode(
    source: str = Path(..., description="Source identifier"),
    season_num: int = Path(..., description="Season number", ge=1),
    episode_num: int = Path(..., description="Episode number", ge=1),
    url: str = Query(..., description="Anime URL path"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get details for a specific episode.

    Returns detailed information for a specific episode within a season,
    including title, URL, tags, and metadata.
    For AniWorld sources, automatically includes AniList metadata enrichment.
    """
    try:
        # Enable metadata for AniWorld sources
        include_metadata = source.lower() == "aniworld"
        async with enhanced_service:
            series_detail = await enhanced_service.get_series_detail(
                source, url, include_metadata
            )
        for season in series_detail.series.seasons:
            if season.season == season_num:
                for episode in season.episodes:
                    if episode.episode == episode_num:
                        return EpisodeResponse(episode=episode)
                raise HTTPException(
                    status_code=404,
                    detail=f"Episode {episode_num} not found in season {season_num}",
                )
        raise HTTPException(status_code=404, detail=f"Season {season_num} not found")
    except HTTPException:
        # Re-raise HTTPExceptions (like our 404) without wrapping them
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


@router.get(
    "/{source}/series/movies",
    response_model=MoviesResponse,
    summary="📺 Get All Movies/OVAs",
    description="**Series Structure**: Get list of all movies, OVAs, and specials for a series, sorted by number. AniWorld responses automatically include AniList metadata.",
    response_description="List of movies, OVAs, and specials",
    operation_id="get_all_movies",
    responses={
        200: {
            "description": "Successfully retrieved movies",
            "content": {
                "application/json": {
                    "example": {
                        "movies": [
                            {
                                "number": 12,
                                "title": "The Last Attack",
                                "kind": "movie",
                                "url": "/anime/stream/attack-on-titan/filme/film-12",
                                "date_upload": None,
                                "tags": [],
                            },
                            {
                                "number": 11,
                                "title": "Great need",
                                "kind": "ova",
                                "url": "/anime/stream/attack-on-titan/filme/film-11",
                                "date_upload": None,
                                "tags": [],
                            },
                        ]
                    }
                }
            },
        }
    },
    tags=["media-api"],
)
async def get_series_movies(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get all movies, OVAs, and specials for a series.

    Returns a complete list of all non-episodic content including movies,
    OVAs (Original Video Animations), and special episodes, sorted by number.
    For AniWorld sources, automatically includes AniList metadata enrichment.
    """
    try:
        # Enable metadata for AniWorld sources
        include_metadata = source.lower() == "aniworld"
        async with enhanced_service:
            series_detail = await enhanced_service.get_series_detail(
                source, url, include_metadata
            )
        return MoviesResponse(movies=series_detail.series.movies)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }


@router.get(
    "/{source}/series/movies/{movie_num}",
    response_model=MovieResponse,
    summary="📺 Get Specific Movie/OVA",
    description="**Series Structure**: Get details for a specific movie, OVA, or special by number, including title, kind, URL, and tags. AniWorld responses automatically include AniList metadata.",
    response_description="Movie/OVA/special details",
    operation_id="get_movie_detail",
    responses={404: {"description": "Movie not found"}},
    tags=["media-api"],
)
async def get_series_movie(
    source: str = Path(..., description="Source identifier"),
    movie_num: int = Path(..., description="Movie/OVA number", ge=1),
    url: str = Query(..., description="Anime URL path"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """
    Get details for a specific movie, OVA, or special.

    Returns detailed information for a specific movie/OVA/special by its number,
    including title, kind (movie/ova/special), URL, and tags.
    For AniWorld sources, automatically includes AniList metadata enrichment.
    """
    try:
        # Enable metadata for AniWorld sources
        include_metadata = source.lower() == "aniworld"
        async with enhanced_service:
            series_detail = await enhanced_service.get_series_detail(
                source, url, include_metadata
            )
        for movie in series_detail.series.movies:
            if movie.number == movie_num:
                return MovieResponse(movie=movie)
        raise HTTPException(status_code=404, detail=f"Movie {movie_num} not found")
    except HTTPException:
        # Re-raise HTTPExceptions (like our 404) without wrapping them
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== METADATA MANAGEMENT ENDPOINTS ==========


@router.get(
    "/metadata/stats",
    summary="📊 Get Metadata Statistics",
    description="**Metadata Analytics**: Get statistics about AniList metadata enrichment performance including match rates and cache efficiency.",
    operation_id="get_metadata_stats",
    tags=["metadata"],
)
async def get_metadata_statistics(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get metadata enrichment statistics."""
    stats = enhanced_service.get_metadata_stats()
    if not stats:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return stats


@router.get(
    "/metadata/cache/info",
    summary="📊 Get Cache Information",
    description="**Cache Analytics**: Get detailed information about the metadata cache including size, hit rate, and configuration.",
    operation_id="get_cache_info",
    tags=["metadata"],
)
async def get_cache_info(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Get cache information and statistics."""
    cache_info = enhanced_service.get_cache_info()
    if not cache_info:
        raise HTTPException(status_code=503, detail="Metadata service not available")
    return cache_info


@router.post(
    "/metadata/cache/clear",
    summary="🗑️ Clear Metadata Cache",
    description="**Cache Management**: Clear the AniList metadata cache to force fresh lookups.",
    operation_id="clear_metadata_cache",
    tags=["metadata"],
)
async def clear_metadata_cache(
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Clear the metadata cache."""
    enhanced_service.clear_metadata_cache()
    return {"message": "Metadata cache cleared successfully"}


@router.post(
    "/metadata/toggle",
    summary="⚙️ Toggle Metadata Enrichment",
    description="**Configuration**: Enable or disable AniList metadata enrichment globally.",
    operation_id="toggle_metadata_enrichment",
    tags=["metadata"],
)
async def toggle_metadata_enrichment(
    enabled: bool = Query(..., description="Enable metadata enrichment"),
    enhanced_service: MediaService = Depends(get_enhanced_anime_service),
):
    """Toggle metadata enrichment on/off."""
    enhanced_service.set_metadata_enabled(enabled)
    return {
        "message": f"Metadata enrichment {'enabled' if enabled else 'disabled'}",
        "metadata_enabled": enhanced_service.enable_metadata,
    }
