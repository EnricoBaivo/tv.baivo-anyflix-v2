"""Base models for anime backend service."""

from __future__ import annotations

from enum import Enum

# Import external data types for union typing
from typing import Any

from pydantic import BaseModel, Field


class MediaSource(BaseModel):
    """Configuration for a media source."""

    name: str
    lang: str
    base_url: str
    api_url: str = ""
    icon_url: str = ""
    type_source: str = "single"
    item_type: int = 1
    is_nsfw: bool = False
    version: str
    date_format: str = ""
    date_format_locale: str = ""
    pkg_path: str


class MovieKind(str, Enum):
    """Movie kind enumeration."""

    MOVIE = "movie"
    OVA = "ova"
    SPECIAL = "special"


class MatchSource(str, Enum):
    """Match source enumeration."""

    TMDB = "tmdb"
    ANILIST = "anilist"


class Episode(BaseModel):
    """Episode information."""

    # For regular episodes
    season: int | None = None
    episode: int | None = None

    # For movies/specials
    kind: str | None = None  # "series", "movie", "ova", "special"
    number: int | None = None  # Film number for movies

    # Common fields
    title: str
    name: str | None = None
    url: str
    tags: list[str] | None = Field(default_factory=list)


class Season(BaseModel):
    """Season information."""

    season: int
    title: str | None = None
    episodes: list[Episode] = Field(default_factory=list)


class Movie(BaseModel):
    """Movie/OVA/Special information."""

    number: int
    title: str
    kind: MovieKind
    url: str
    date_upload: str | None = None
    tags: list[str] = Field(default_factory=list)


class SeriesDetail(BaseModel):
    """Hierarchical series detail with seasons and movies."""

    slug: str
    seasons: list[Season] = Field(default_factory=list)
    movies: list[Movie] = Field(default_factory=list)


class MediaInfo(BaseModel):
    """Detailed Media information."""

    name: str
    cover_image_url: str
    description: str
    author: str = ""
    genres: list[str] = Field(default_factory=list)
    episodes: list[Episode] = Field(default_factory=list)  # Internal use only
    seasons_length: int | None = Field(None, description="Number of episodes")
    # Extended metadata fields from seriesContentBox
    alternative_titles: list[str] = Field(
        default_factory=list, description="Alternative titles in different languages"
    )
    start_year: int | None = Field(None, description="Start year of the series")
    end_year: int | None = Field(None, description="End year of the series")
    fsk_rating: int | None = Field(
        None, description="FSK age rating (German rating system)"
    )
    imdb_id: str | None = Field(None, description="IMDB ID (e.g., 'tt36469298')")
    country_of_origin: str | None = Field(None, description="Country of origin")
    main_genre: str | None = Field(None, description="Primary genre classification")
    directors: list[str] = Field(default_factory=list, description="List of directors")
    actors: list[str] = Field(default_factory=list, description="List of main actors")
    producers: list[str] = Field(
        default_factory=list, description="List of production companies"
    )
    backdrop_url: str | None = Field(None, description="Backdrop/banner image URL")
    series_id: str | None = Field(
        None, description="Internal series ID from the provider"
    )


class SearchResult(BaseModel):
    """Search result item."""

    name: str
    image_url: str
    link: str

    media_info: MediaInfo | None = None
    best_match: Any | None = None
    best_match_source: MatchSource | None = None
    confidence: float | None = None


class VideoSource(BaseModel):
    """Video source information."""

    url: str
    original_url: str
    quality: str
    language: str | None = None
    type: str | None = None  # "Dub" or "Sub"
    host: str | None = None  # Video host name (e.g., "vidmoly", "voe", "doodstream")
    requires_proxy: bool = False  # Whether this source requires proxy due to CORS
    headers: dict[str, str] | None = None
    subtitles: list[dict[str, str]] | None = None
    audios: list[dict[str, str]] | None = None


class SourcePreference(BaseModel):
    """Source preference configuration."""

    key: str
    list_preference: dict[str, Any] | None = None
    multi_select_list_preference: dict[str, Any] | None = None


# Rebuild models with forward references after all models are defined
def rebuild_models() -> None:
    """Rebuild models with forward references."""
    SearchResult.model_rebuild()
