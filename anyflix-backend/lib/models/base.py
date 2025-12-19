"""Base models for anime backend service."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from lib.models.tmdb import (  # noqa: TC001 - Pydantic needs these at runtime
    TMDBEpisodeDetail,
    TMDBMovieDetail,
    TMDBSearchResult,
    TMDBSeasonDetail,
    TMDBTVDetail,
)


class ContentType(str, Enum):
    """Content type enumeration for media sources."""

    ANIME = "anime"
    SERIES_MOVIE = "series_movie"
    ADULT = "adult"
    UNKNOWN = "unknown"


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


class Episode(BaseModel):
    """Episode information (base model without TMDB enrichment)."""

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


# ============================================================================
# Enriched Models with Embedded TMDB Data
# ============================================================================


class EnrichedEpisode(BaseModel):
    """Episode with embedded TMDB episode data.

    This model extends the base Episode with full TMDB episode details
    including crew, guest_stars, videos, and images.
    """

    # Provider fields (regular episodes)
    season: int | None = Field(None, description="Season number for series episodes")
    episode: int | None = Field(None, description="Episode number within season")

    # Provider fields (movies/specials)
    kind: str | None = Field(
        None, description="Content kind: 'series', 'movie', 'ova', 'special'"
    )
    number: int | None = Field(None, description="Film number for movie collections")

    # Common provider fields
    title: str = Field(..., description="Episode title from provider")
    name: str | None = Field(None, description="Alternative episode name")
    url: str = Field(..., description="Streaming URL path")
    tags: list[str] = Field(default_factory=list, description="Provider-specific tags")

    # Embedded TMDB data (new structure)
    tmdb_episode_data: TMDBEpisodeDetail | None = Field(
        None,
        description="Complete TMDB episode details including crew, guest_stars, videos, images",
    )


class EnrichedSeason(BaseModel):
    """Season with embedded TMDB season data.

    This model extends the base Season with full TMDB season details
    and uses EnrichedEpisode for episodes.
    """

    # Provider fields
    season: int = Field(..., description="Season number (0 for specials)")
    title: str | None = Field(None, description="Season title from provider")
    episodes: list[EnrichedEpisode] = Field(
        default_factory=list,
        description="List of episodes with optional TMDB enrichment",
    )

    # Embedded TMDB data (new structure)
    tmdb_season_data: TMDBSeasonDetail | None = Field(
        None,
        description="Complete TMDB season details including metadata, poster, videos, images",
    )
    episode_count: int | None = Field(
        None,
        description="Total episode count from TMDB (may differ from episodes list length)",
    )


class EnrichedSeriesDetail(BaseModel):
    """Hierarchical series detail with embedded TMDB data at all levels.

    This is the top-level enriched model that contains:
    - EnrichedSeasons with tmdb_season_data
    - EnrichedEpisodes with tmdb_episode_data
    - Series-level tmdb_series_data
    """

    slug: str
    seasons: list[EnrichedSeason] = Field(default_factory=list)
    movies: list[Movie] = Field(default_factory=list)

    # Embedded TMDB data at series level
    tmdb_series_data: TMDBTVDetail | None = Field(
        None,
        description="Complete TMDB TV series details",
    )
    match_confidence: float | None = Field(
        None,
        ge=0,
        le=1,
        description="Confidence score of TMDB match (0-1)",
    )


class MediaInfo(BaseModel):
    """Detailed Media information."""

    name: str
    cover_image_url: str
    description: str
    genres: list[str] = Field(default_factory=list)
    episodes: list[Episode] = Field(default_factory=list)  # Internal use only
    seasons_length: int | None = Field(None, description="Number of seasons")
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
    trailer_url: str | None = Field(None, description="Trailer or official website URL")
    rating_value: float | None = Field(None, description="User rating value (e.g., 3.0)")
    rating_count: int | None = Field(None, description="Number of user ratings")
    available_languages: list[str] = Field(
        default_factory=list,
        description="Available languages/audio tracks (de, en, de_sub, en_sub)",
    )


class TMDBMediaResult(BaseModel):
    """TMDB media result model."""

    media_result: TMDBSearchResult
    media_info: TMDBMovieDetail | TMDBTVDetail


class SearchResult(BaseModel):
    """Search result item."""

    name: str
    image_url: str
    link: str
    provider: str
    available_languages: list[str] = Field(
        default_factory=list, description="Available languages (de, en, sub, jp)"
    )
    media_info: MediaInfo | None = None


class VideoSource(BaseModel):
    """Video source information."""

    url: str
    original_url: str
    quality: str
    language: str | None = None
    format: str | None = None
    type: str | None = Field(
        default="original", description="Dub or Sub or original"
    )  # "Dub" or "Sub"
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
