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

# Response models
from .responses import (
    EpisodeResponse,
    MovieResponse,
    MoviesResponse,
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
    "MovieResponse",
    "MoviesResponse",
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
