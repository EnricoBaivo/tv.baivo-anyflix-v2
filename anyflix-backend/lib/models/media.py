from enum import Enum

from pydantic import BaseModel, Field

from lib.models.base import MatchSource


class MediaFormat(str, Enum):
    """Media format enumeration."""

    TV = "TV"
    TV_SHORT = "TV_SHORT"
    MOVIE = "MOVIE"
    SPECIAL = "SPECIAL"
    OVA = "OVA"
    ONA = "ONA"
    MUSIC = "MUSIC"
    MANGA = "MANGA"
    NOVEL = "NOVEL"
    ONE_SHOT = "ONE_SHOT"


class MediaSeason(str, Enum):
    """Media season enumeration."""

    WINTER = "WINTER"
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    FALL = "FALL"


class RankingType(str, Enum):
    """Ranking type enumeration."""

    RATED = "RATED"
    POPULAR = "POPULAR"


class MediaRankingContext(str, Enum):
    """Media ranking context enumeration."""

    HIGHEST_RATED_ALL_TIME = "highest rated all time"
    HIGHEST_RATED = "highest rated"
    MOST_POPULAR = "most popular"
    MOST_POPULAR_ALL_TIME = "most popular all time"


class MediaStatus(str, Enum):
    """Media status enumeration."""

    FINISHED = "FINISHED"
    RELEASING = "RELEASING"
    NOT_YET_RELEASED = "NOT_YET_RELEASED"
    CANCELLED = "CANCELLED"
    HIATUS = "HIATUS"


class MediaRanking(BaseModel):
    """Media ranking model."""

    id: int
    rank: int
    type: RankingType
    format: MediaFormat
    year: int | None = None
    season: MediaSeason | None = None
    allTime: bool | None = None
    context: str


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
    tmdb_id: int | None = None
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
