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
from .base import (
    Episode,
    MatchSource,
    MediaInfo,
    SearchResult,
    SourcePreference,
    VideoSource,
    rebuild_models,
)

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

# Rebuild models with forward references after all imports
rebuild_models()

__all__ = [
    "Episode",
    # Response models
    "EpisodeResponse",
    "LatestResponse",
    "MatchSource",
    # AniList models
    "Media",
    # Base models
    "MediaInfo",
    "MediaPageResponse",
    "MediaResponse",
    "MediaSearchVariables",
    "MediaType",
    "MovieResponse",
    "MoviesResponse",
    "PageResponse",
    "PopularResponse",
    "SearchResponse",
    "SearchResult",
    "SeasonResponse",
    "SeasonsResponse",
    "SeriesDetailResponse",
    "SourcePreference",
    # TMDB models
    "TMDBConfiguration",
    "TMDBMovieDetail",
    "TMDBSearchResponse",
    "TMDBSearchResult",
    "TMDBTVDetail",
    "VideoListResponse",
    "VideoSource",
]
