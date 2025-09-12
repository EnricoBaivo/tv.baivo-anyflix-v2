"""Models for anime backend service."""

# AniList models
from .anilist import (
    Media,
    MediaPageResponse,
    MediaResponse,
    MediaSearchVariables,
    MediaType,
    PageResponse,
)

# Base models
from .base import Episode, MediaInfo, SearchResult, SourcePreference, VideoSource

# Metadata stats (moved to enhanced.py)
# Enhanced models (new structure)
from .enhanced import (
    EnhancedDetailResponse,
    EnhancedLatestResponse,
    EnhancedMediaInfo,
    EnhancedPopularResponse,
    EnhancedSearchResponse,
    EnhancedSearchResult,
    EnhancedSeriesDetail,
    EnhancedSeriesDetailResponse,
    EnhancedVideoListResponse,
    MetadataStats,
)

# Response models
from .responses import (
    LatestResponse,
    PopularResponse,
    SearchResponse,
    VideoListResponse,
)

__all__ = [
    # AniList models
    "Media",
    "MediaPageResponse",
    "MediaResponse",
    "MediaSearchVariables",
    "MediaType",
    "PageResponse",
    # Base models
    "MediaInfo",
    "Episode",
    "VideoSource",
    "SearchResult",
    "SourcePreference",
    # Enhanced models
    "EnhancedDetailResponse",
    "EnhancedLatestResponse",
    "EnhancedMediaInfo",
    "EnhancedPopularResponse",
    "EnhancedSearchResponse",
    "EnhancedSearchResult",
    "EnhancedSeriesDetail",
    "EnhancedSeriesDetailResponse",
    "EnhancedVideoListResponse",
    # Generic models
    "MetadataStats",
    # Response models
    "PopularResponse",
    "LatestResponse",
    "SearchResponse",
    "VideoListResponse",
]
