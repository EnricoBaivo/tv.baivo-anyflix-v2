"""Base models for anime backend service."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from lib.models.tmdb import TMDBMovieDetail, TMDBTVDetail

if TYPE_CHECKING:
    from lib.models.anilist import Media  # noqa: F401
    from lib.models.tmdb import TMDBSearchResult  # noqa: F401

# Type alias using string annotations for runtime compatibility
# This approach provides several benefits:
# 1. Avoids circular import issues at runtime
# 2. Keeps type checking accurate during development
# 3. Allows for cleaner dependency separation
# 4. Maintains backward compatibility


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
    """Match source enumeration. Can be TMDB, ANILIST or both."""

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
    media_info: MediaInfo | None = None
    anilist_media_info: Media | None = None
    tmdb_media_info: TMDBMediaResult | None = None
    best_match_source: MatchSource | None = None
    confidence: float | None = None
    is_anime: bool = Field(
        default=False, description="Is currently detecting with provider"
    )


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


# Rebuild models with forward references after all models are defined
def rebuild_models() -> None:
    """Rebuild models with forward references."""
    # Import the actual classes for rebuilding
    import sys

    from lib.models.anilist import Media
    from lib.models.tmdb import TMDBSearchResult

    # Add the types to the global namespace for proper resolution
    module = sys.modules[__name__]
    module.Media = Media  # type: ignore[attr-defined]
    module.TMDBSearchResult = TMDBSearchResult  # type: ignore[attr-defined]

    # Rebuild the base model first
    SearchResult.model_rebuild()

    # Also rebuild dependent models that use SearchResult
    try:
        from lib.models.responses import PaginatedResponse

        PaginatedResponse.model_rebuild()
    except ImportError:
        pass  # responses module might not be available in all contexts
