"""Response models for API endpoints."""

from typing import Generic, TypeVar

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

    videos: list[VideoSource]


class SeriesDetailResponse(BaseModel):
    """Response for hierarchical series detail."""

    series: SeriesDetail


class SeasonsResponse(BaseModel):
    """Response for seasons list."""

    seasons: list[Season]


class SeasonResponse(BaseModel):
    """Response for single season."""

    season: Season


class EpisodeResponse(BaseModel):
    """Response for single episode."""

    episode: Episode


class MoviesResponse(BaseModel):
    """Response for movies list."""

    movies: list[Movie]


class MovieResponse(BaseModel):
    """Response for single movie."""

    movie: Movie
