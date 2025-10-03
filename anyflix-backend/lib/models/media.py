from enum import Enum

from pydantic import BaseModel, Field

from lib.models.anilist import MediaFormat, MediaRanking
from lib.models.base import MatchSource


class MediaSourceEnum(Enum):
    """Source media type. series or movie."""

    SERIES = "series"
    MOVIE = "movie"
    OVA = "ova"
    SPECIAL = "special"


class MediaStatusEnum(Enum):
    """Media status type."""

    COMPLETED = "completed"
    CONTINUING = "continuing"
    RELEASED = "released"


class MediaSpotlight(BaseModel):
    """Media spotlight model."""

    id: str
    title: str
    description: str
    media_source_type: MediaSourceEnum = Field(
        default=MediaSourceEnum.SERIES,
        description="Source media type. series or movie.",
    )
    image_cover_url: str
    image_backdrop_url: str | None = None
    color: str | None = None
    logo_urls: list[str] | None = None
    release_year: int
    average_rating: int | float = Field(default=0, ge=0, le=100)  # max 100%
    popularity: int | float = Field(default=0, ge=0)  # max 100%
    votes: int = Field(default=0, ge=0)
    best_ranking: MediaRanking | None = Field(
        default=None,
        description="Best ranking for the media only available for anime sources",
    )
    media_status: MediaStatusEnum
    genres: list[str]
    seasons_count: int | None = None
    episodes_count: int | None = None
    fsk_rating: int | None = None
    media_format: MediaFormat = Field(
        default=None,
        description="Media format for the media only available for anime sources",
    )
    source: MatchSource | None = None
    provider_url: str
    provider: str
    trailers: list[str] | None = Field(
        default=None,
        description="Trailers for the media as a youtube url",
    )
    clips: list[str] | None = Field(
        default=None,
        description="Clips for the media as a youtube url",
    )
    teasers: list[str] | None = Field(
        default=None,
        description="Teasers for the media as a youtube url",
    )
