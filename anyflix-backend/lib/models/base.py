"""Base models for anime backend service."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl


class AnimeSource(BaseModel):
    """Configuration for an anime source."""

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


class Episode(BaseModel):
    """Episode information."""

    season: int
    episode: int
    title: str
    url: str
    date_upload: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class Season(BaseModel):
    """Season information."""

    season: int
    title: Optional[str] = None
    episodes: List[Episode] = Field(default_factory=list)


class Movie(BaseModel):
    """Movie/OVA/Special information."""

    number: int
    title: str
    kind: MovieKind
    url: str
    date_upload: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class SeriesDetail(BaseModel):
    """Hierarchical series detail with seasons and movies."""

    slug: str
    seasons: List[Season] = Field(default_factory=list)
    movies: List[Movie] = Field(default_factory=list)


class AnimeInfo(BaseModel):
    """Detailed anime information."""

    name: str
    image_url: str
    description: str
    author: str = ""
    status: int = 5
    genre: List[str] = Field(default_factory=list)
    episodes: List[Dict[str, Any]] = Field(default_factory=list)  # Internal use only


class SearchResult(BaseModel):
    """Search result item."""

    name: str
    image_url: str
    link: str


class VideoSource(BaseModel):
    """Video source information."""

    url: str
    original_url: str
    quality: str
    language: Optional[str] = None
    type: Optional[str] = None  # "Dub" or "Sub"
    host: Optional[str] = None  # Video host name (e.g., "vidmoly", "voe", "doodstream")
    requires_proxy: bool = False  # Whether this source requires proxy due to CORS
    headers: Optional[Dict[str, str]] = None
    subtitles: Optional[List[Dict[str, str]]] = None
    audios: Optional[List[Dict[str, str]]] = None


class SourcePreference(BaseModel):
    """Source preference configuration."""

    key: str
    list_preference: Optional[Dict[str, Any]] = None
    multi_select_list_preference: Optional[Dict[str, Any]] = None
