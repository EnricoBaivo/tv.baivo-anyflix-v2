"""Enhanced models using composition and mixins."""

from typing import Optional, TypeVar

from pydantic import BaseModel, Field

from .base import MediaInfo, SearchResult, SeriesDetail, VideoSource
from .mixins import AniListMixin, DetailedMetadataMixin, EnhancedMetadataMixin
from .responses import PaginatedResponse

# Define TypeVar for generic types
T = TypeVar("T")


class EnhancedSearchResult(SearchResult, AniListMixin):
    """Enhanced search result with AniList metadata."""

    pass


class EnhancedMediaInfo(MediaInfo, AniListMixin, EnhancedMetadataMixin):
    """Enhanced media information with AniList metadata."""

    pass


class EnhancedSeriesDetail(SeriesDetail, AniListMixin, DetailedMetadataMixin):
    """Enhanced series detail with AniList metadata."""

    pass


class EnhancedVideoListResponse(BaseModel):
    """Enhanced response for video sources with metadata context."""

    videos: list[VideoSource]

    # Optional context about the anime
    anime_context: Optional[dict] = Field(
        None, description="Basic anime information for context"
    )
    episode_context: Optional[dict] = Field(
        None, description="Episode-specific information"
    )


# Enhanced pagination patterns
class EnhancedPaginatedResponse(PaginatedResponse[T]):
    """Enhanced paginated response with metadata coverage."""

    metadata_coverage: Optional[float] = Field(
        None, description="Percentage of results with AniList metadata"
    )


class SearchPaginatedResponse(EnhancedPaginatedResponse[T]):
    """Search-specific paginated response with total count."""

    total_results: Optional[int] = Field(
        None, description="Total number of results found"
    )


# Response type aliases using generics

EnhancedPopularResponse = EnhancedPaginatedResponse[EnhancedSearchResult]
EnhancedLatestResponse = EnhancedPaginatedResponse[EnhancedSearchResult]
EnhancedSearchResponse = SearchPaginatedResponse[EnhancedSearchResult]


# Single item response models
class EnhancedDetailResponse(BaseModel):
    """Enhanced response for media details with metadata."""

    media: EnhancedMediaInfo


class EnhancedSeriesDetailResponse(BaseModel):
    """Enhanced response for hierarchical series detail with metadata."""

    series: EnhancedSeriesDetail


class MetadataStats(BaseModel):
    """Statistics about metadata enrichment."""

    total_requests: int
    anilist_matches: int
    match_rate: float = Field(description="Percentage of successful AniList matches")
    average_confidence: Optional[float] = Field(
        None, description="Average match confidence score"
    )
    cache_hits: int = 0
    cache_misses: int = 0
