"""Response models for API endpoints."""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

from .anilist import Media
from .base import (
    Episode,
    MediaInfo,
    Movie,
    SearchResult,
    Season,
    SeriesDetail,
    VideoSource,
)
from .tmdb import TMDBMovieDetail, TMDBTVDetail

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
    tmdb_data: Optional[TMDBMovieDetail | TMDBTVDetail] = None
    anilist_data: Optional[Media] = None
    match_confidence: Optional[float] = None
    length: Optional[int] = None
    series: SeriesDetail


class SeasonsResponse(BaseModel):
    """Response for seasons list."""

    type: str  # "anime" or "normal"
    seasons: list[Season]
    tmdb_data: Optional[TMDBMovieDetail | TMDBTVDetail] = None
    anilist_data: Optional[Media] = None
    match_confidence: Optional[float] = None


class SeasonResponse(BaseModel):
    """Response for single season."""

    type: str  # "anime" or "normal"
    tmdb_data: Optional[TMDBMovieDetail | TMDBTVDetail] = None
    anilist_data: Optional[Media] = None
    season: Season


class EpisodeResponse(BaseModel):
    """Response for single episode."""

    type: str  # "anime" or "normal"
    tmdb_data: Optional[TMDBMovieDetail | TMDBTVDetail] = None
    anilist_data: Optional[Media] = None
    episode: Episode


class MoviesResponse(BaseModel):
    """Response for movies list."""

    type: str  # "anime" or "normal"
    movies: list[Movie]
    tmdb_data: Optional[TMDBMovieDetail | TMDBTVDetail] = None
    anilist_data: Optional[Media] = None
    match_confidence: Optional[float] = None


class MovieResponse(BaseModel):
    """Response for single movie."""

    type: str  # "anime" or "normal"
    movie: Movie
    tmdb_data: Optional[TMDBMovieDetail | TMDBTVDetail] = None
    anilist_data: Optional[Media] = None
    match_confidence: Optional[float] = None


class TrailerRequest(BaseModel):
    """Request model for trailer extraction."""

    # AniList trailer data
    anilist_trailer: Optional[Dict[str, Any]] = None
    # TMDB trailer data
    tmdb_trailer: Optional[Dict[str, Any]] = None


class TrailerResponse(BaseModel):
    """Response for trailer extraction."""

    success: bool
    original_url: str
    streamable_url: Optional[str] = None
    quality: Optional[str] = None
    site: Optional[str] = None
    error: Optional[str] = None


class SourcesResponse(BaseModel):
    """Response for available sources list."""

    sources: List[str] = Field(description="List of available source names")


class PreferencesResponse(BaseModel):
    """Response for source preferences/configuration."""

    preferences: Dict[str, Any] = Field(description="Source configuration preferences")
