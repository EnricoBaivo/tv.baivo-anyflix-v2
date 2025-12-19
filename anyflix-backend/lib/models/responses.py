"""Response models for API endpoints."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from .base import (
    ContentType,
    EnrichedEpisode,
    EnrichedSeason,
    EnrichedSeriesDetail,
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

# Generic type for API envelope
T = TypeVar("T")


# ============================================================================
# Standard API Response Envelope
# ============================================================================


class ApiMetadata(BaseModel):
    """Standard metadata for all API responses."""

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp (UTC)")
    request_id: str | None = Field(None, description="Unique request identifier for tracking")
    version: str = Field("1.0.0", description="API version")

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class ApiError(BaseModel):
    """Standard error format."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error context")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standard API response envelope for all endpoints.

    Provides consistent structure with:
    - Success/error status
    - Standard metadata (timestamp, request_id, version)
    - Typed data payload
    - Error information when applicable
    """

    success: bool = Field(..., description="Whether the request was successful")
    data: T | None = Field(None, description="Response payload data")
    error: ApiError | None = Field(None, description="Error information if request failed")
    metadata: ApiMetadata = Field(default_factory=ApiMetadata, description="Response metadata")


# ============================================================================
# Pagination Models
# ============================================================================


class PaginationMetadata(BaseModel):
    """Pagination metadata for list responses."""

    page: int = Field(..., ge=1, description="Current page number (1-based)")
    per_page: int = Field(..., ge=1, description="Items per page")
    total_items: int | None = Field(None, description="Total number of items across all pages")
    total_pages: int | None = Field(None, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedData(BaseModel, Generic[T]):
    """Generic paginated data container."""

    items: list[T] = Field(..., description="List of items for current page")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


# Paginated response models - concrete classes instead of generics
class PaginatedSearchResultResponse(BaseModel):
    """Paginated response for search results with comprehensive metadata."""

    content_type: ContentType = Field(..., description="Type of content (anime, series_movie, adult)")
    items: list[SearchResult] = Field(..., description="Search result items for current page")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")

    model_config = {"json_schema_extra": {
        "examples": [{
            "content_type": "anime",
            "items": [
                {
                    "name": "Attack on Titan",
                    "image_url": "https://example.com/image.jpg",
                    "link": "/anime/stream/attack-on-titan",
                    "provider": "AniWorld",
                    "available_languages": ["de", "de_sub"]
                }
            ],
            "pagination": {
                "page": 1,
                "per_page": 15,
                "total_items": 100,
                "total_pages": 7,
                "has_next": True,
                "has_previous": False
            }
        }]
    }}


# ============================================================================
# Single Item Responses
# ============================================================================


class DetailResponse(BaseModel):
    """Response for media details."""

    media: SearchResult


class VideoListResponse(BaseModel):
    """Response for video sources."""

    content_type: ContentType = Field(..., description="Type of content (anime, series_movie, adult)")
    videos: list[VideoSource] = Field(..., description="Available video sources")


class SeriesDetailResponse(BaseModel):
    """Response for hierarchical series detail with TMDB enrichment."""

    content_type: ContentType = Field(
        ..., description="Type of content (anime, series_movie, adult)"
    )
    series: SeriesDetail = Field(..., description="Series detail with seasons and movies")
    season_count: int | None = Field(None, description="Total number of seasons")

    tmdb_series_data: TMDBTVDetail | None = Field(
        None, description="Complete TMDB TV series details"
    )
    match_confidence: float | None = Field(
        None, ge=0, le=1, description="Confidence score of TMDB match (0-1)"
    )


class SeasonsResponse(BaseModel):
    """Response for seasons list with embedded TMDB data."""

    content_type: ContentType = Field(
        ..., description="Type of content (anime, series_movie, adult)"
    )
    seasons: list[EnrichedSeason] = Field(
        ..., description="List of all seasons with embedded TMDB data per season"
    )

    tmdb_series_data: TMDBTVDetail | None = Field(
        None, description="Complete TMDB TV series details"
    )
    match_confidence: float | None = Field(
        None, ge=0, le=1, description="Confidence score of TMDB match (0-1)"
    )


class SeasonResponse(BaseModel):
    """Response for single season with embedded TMDB data."""

    content_type: ContentType = Field(
        ..., description="Type of content (anime, series_movie, adult)"
    )
    season: EnrichedSeason = Field(
        ..., description="Season detail with episodes and embedded TMDB season data"
    )

    tmdb_series_data: TMDBTVDetail | None = Field(
        None, description="Complete TMDB TV series details for context"
    )
    match_confidence: float | None = Field(
        None, ge=0, le=1, description="Confidence score of TMDB match (0-1)"
    )


class EpisodeResponse(BaseModel):
    """Response for single episode with embedded TMDB data."""

    content_type: ContentType = Field(
        ..., description="Type of content (anime, series_movie, adult)"
    )
    episode: EnrichedEpisode = Field(
        ..., description="Episode details with embedded TMDB episode data"
    )

    tmdb_series_data: TMDBTVDetail | None = Field(
        None, description="Complete TMDB TV series details for context"
    )
    match_confidence: float | None = Field(
        None, ge=0, le=1, description="Confidence score of TMDB match (0-1)"
    )


class MoviesResponse(BaseModel):
    """Response for movies list."""

    content_type: ContentType = Field(
        ..., description="Type of content (anime, series_movie, adult)"
    )
    movies: list[Movie] = Field(..., description="List of movies, OVAs, and specials")

    tmdb_series_data: TMDBTVDetail | TMDBMovieDetail | None = Field(
        None, description="Complete TMDB series or movie details"
    )
    match_confidence: float | None = Field(
        None, ge=0, le=1, description="Confidence score of TMDB match (0-1)"
    )


class MovieResponse(BaseModel):
    """Response for single movie."""

    content_type: ContentType = Field(
        ..., description="Type of content (anime, series_movie, adult)"
    )
    movie: Movie = Field(..., description="Movie details")

    tmdb_series_data: TMDBMovieDetail | None = Field(
        None, description="Complete TMDB movie details"
    )
    match_confidence: float | None = Field(
        None, ge=0, le=1, description="Confidence score of TMDB match (0-1)"
    )


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
