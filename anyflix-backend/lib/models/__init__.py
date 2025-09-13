"""Models for media backend service."""

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

# Response models
from .responses import (
    EpisodeResponse,
    LatestResponse,
    MovieResponse,
    MoviesResponse,
    PopularResponse,
    SearchResponse,
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
    "EpisodeResponse",
    "LatestResponse",
    "MovieResponse",
    "MoviesResponse",
    "PopularResponse",
    "SearchResponse",
    "SeasonResponse",
    "SeasonsResponse",
    "SeriesDetailResponse",
    "VideoListResponse",
    # TMDB models
    "TMDBConfiguration",
    "TMDBMovieDetail",
    "TMDBSearchResponse",
    "TMDBSearchResult",
    "TMDBTVDetail",
]
