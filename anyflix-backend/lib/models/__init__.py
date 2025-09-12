"""Models for anime backend service."""

from .anilist import (
    Media,
    MediaPageResponse,
    MediaResponse,
    MediaSearchVariables,
    MediaType,
    PageResponse,
)
from .base import Episode, MediaInfo, SearchResult, SourcePreference, VideoSource
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
    # Response models
    "PopularResponse",
    "LatestResponse",
    "SearchResponse",
    "VideoListResponse",
]
