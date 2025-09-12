"""Response models for API endpoints."""

from typing import List

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


class PopularResponse(BaseModel):
    """Response for popular anime list."""

    list: List[SearchResult]
    has_next_page: bool = False


class LatestResponse(BaseModel):
    """Response for latest updates."""

    list: List[SearchResult]
    has_next_page: bool = False


class SearchResponse(BaseModel):
    """Response for search results."""

    list: List[SearchResult]
    has_next_page: bool = False


class DetailResponse(BaseModel):
    """Response for media details."""

    media: MediaInfo


class VideoListResponse(BaseModel):
    """Response for video sources."""

    videos: List[VideoSource]


class SeriesDetailResponse(BaseModel):
    """Response for hierarchical series detail."""

    series: SeriesDetail


class SeasonsResponse(BaseModel):
    """Response for seasons list."""

    seasons: List[Season]


class SeasonResponse(BaseModel):
    """Response for single season."""

    season: Season


class EpisodeResponse(BaseModel):
    """Response for single episode."""

    episode: Episode


class MoviesResponse(BaseModel):
    """Response for movies list."""

    movies: List[Movie]


class MovieResponse(BaseModel):
    """Response for single movie."""

    movie: Movie
