"""Response models for API endpoints."""

from typing import Any

from pydantic import BaseModel, Field

from .base import (
    Episode,
    Movie,
    SearchResult,
    Season,
    SeriesDetail,
    VideoSource,
)
from .tmdb import (
    TMDBEpisodeDetail,
    TMDBMovieDetail,
    TMDBSeasonDetail,
    TMDBTVDetail,
)


# Paginated response models - concrete classes instead of generics
class PaginatedSearchResultResponse(BaseModel):
    """Paginated response for search results."""

    type: str  # "anime" or "normal"
    list: list[SearchResult]
    has_next_page: bool = False


# Single item responses
class DetailResponse(BaseModel):
    """Response for media details."""

    media: SearchResult


class VideoListResponse(BaseModel):
    """Response for video sources."""

    type: str  # "anime" or "normal"
    videos: list[VideoSource]


class SeriesDetailResponse(BaseModel):
    """Response for hierarchical series detail."""

    type: str  # "anime" or "normal"
    tmdb_data: TMDBMovieDetail | TMDBTVDetail | None = None
    match_confidence: float | None = None
    length: int | None = None
    series: SeriesDetail


class SeasonsResponse(BaseModel):
    """Response for seasons list."""

    type: str  # "anime" or "normal"
    seasons: list[Season]
    tmdb_data: TMDBMovieDetail | TMDBTVDetail | None = None
    match_confidence: float | None = None


class SeasonResponse(BaseModel):
    """Response for single season."""

    type: str  # "anime" or "normal"
    tmdb_data: TMDBMovieDetail | TMDBTVDetail | None = None
    tmdb_season: TMDBSeasonDetail | None = None  # Season-specific TMDB data
    season: Season


class EpisodeResponse(BaseModel):
    """Response for single episode."""

    type: str  # "anime" or "normal"
    tmdb_data: TMDBMovieDetail | TMDBTVDetail | None = None
    tmdb_episode: TMDBEpisodeDetail | None = None  # Episode-specific TMDB data
    episode: Episode


class MoviesResponse(BaseModel):
    """Response for movies list."""

    type: str  # "anime" or "normal"
    movies: list[Movie]
    tmdb_data: TMDBMovieDetail | TMDBTVDetail | None = None
    match_confidence: float | None = None


class MovieResponse(BaseModel):
    """Response for single movie."""

    type: str  # "anime" or "normal"
    movie: Movie
    tmdb_data: TMDBMovieDetail | TMDBTVDetail | None = None
    match_confidence: float | None = None


class TrailerRequest(BaseModel):
    """Request model for trailer extraction."""

    tmdb_trailer: dict[str, Any] | None = None


class TrailerResponse(BaseModel):
    """Response for trailer extraction."""

    success: bool
    original_url: str
    streamable_url: str | None = None
    m3u8_url: str | None = None
    quality: str | None = None
    error: str | None = None


class SourcesResponse(BaseModel):
    """Response for available sources list."""

    sources: list[str] = Field(description="List of available source names")


class PreferencesResponse(BaseModel):
    """Response for source preferences/configuration."""

    preferences: dict[str, Any] = Field(description="Source configuration preferences")
