"""Response models for API endpoints."""

from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel

from .base import (
    Episode,
    MediaInfo,
    Movie,
    SearchResult,
    Season,
    SeriesDetail,
    VideoSource,
)

# Generic patterns (moved from generic.py)
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    type: str  # "anime" or "normal"
    list: list[T]
    has_next_page: bool = False


# Type aliases using generics for common patterns
PopularResponse = PaginatedResponse[SearchResult]
LatestResponse = PaginatedResponse[SearchResult]
SearchResponse = PaginatedResponse[SearchResult]


# Single item responses
class DetailResponse(BaseModel):
    """Response for media details."""

    media: MediaInfo


class VideoListResponse(BaseModel):
    """Response for video sources."""

    type: str  # "anime" or "normal"
    videos: list[VideoSource]


class SeriesDetailResponse(BaseModel):
    """Response for hierarchical series detail."""

    type: str  # "anime" or "normal"
    tmdb_data: Optional[Dict[str, Any]] = None
    anilist_data: Optional[Dict[str, Any]] = None
    series: SeriesDetail


class SeasonsResponse(BaseModel):
    """Response for seasons list."""

    seasons: list[Season]


class SeasonResponse(BaseModel):
    """Response for single season."""

    type: str  # "anime" or "normal"
    tmdb_data: Optional[Dict[str, Any]] = None
    anilist_data: Optional[Dict[str, Any]] = None
    season: Season


class EpisodeResponse(BaseModel):
    """Response for single episode."""

    type: str  # "anime" or "normal"
    tmdb_data: Optional[Dict[str, Any]] = None
    anilist_data: Optional[Dict[str, Any]] = None
    episode: Episode


class MoviesResponse(BaseModel):
    """Response for movies list."""

    movies: list[Movie]


class MovieResponse(BaseModel):
    """Response for single movie."""

    movie: Movie
