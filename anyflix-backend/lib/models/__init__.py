"""Models for media backend service."""

# Base models
from .base import (
    Episode,
    MatchSource,
    MediaInfo,
    SearchResult,
    SourcePreference,
    VideoSource,
)

# Media models
from .media import MediaSpotlight

# Response models
from .responses import (
    EpisodeResponse,
    MovieResponse,
    MoviesResponse,
    PaginatedMediaSpotlightResponse,
    PaginatedSearchResultResponse,
    SeasonResponse,
    SeasonsResponse,
    SeriesDetailResponse,
    VideoListResponse,
)

# TMDB models
from .tmdb import (
    TMDBConfiguration,
    TMDBMovieDetail,
    TMDBSearchResponse,
    TMDBSearchResult,
    TMDBTVDetail,
)

__all__ = [
    "Episode",
    "EpisodeResponse",
    "MatchSource",
    "MediaInfo",
    "MediaSpotlight",
    "MovieResponse",
    "MoviesResponse",
    "PaginatedMediaSpotlightResponse",
    "PaginatedSearchResultResponse",
    "SearchResult",
    "SeasonResponse",
    "SeasonsResponse",
    "SeriesDetailResponse",
    "SourcePreference",
    "TMDBConfiguration",
    "TMDBMovieDetail",
    "TMDBSearchResponse",
    "TMDBSearchResult",
    "TMDBTVDetail",
    "VideoListResponse",
    "VideoSource",
]
