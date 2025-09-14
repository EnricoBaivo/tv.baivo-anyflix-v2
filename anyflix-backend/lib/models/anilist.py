"""AniList API models for GraphQL responses."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, field_validator


class MediaType(str, Enum):
    """Media type enumeration."""

    ANIME = "ANIME"
    MANGA = "MANGA"


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


class MediaStatus(str, Enum):
    """Media status enumeration."""

    FINISHED = "FINISHED"
    RELEASING = "RELEASING"
    NOT_YET_RELEASED = "NOT_YET_RELEASED"
    CANCELLED = "CANCELLED"
    HIATUS = "HIATUS"


class MediaSeason(str, Enum):
    """Media season enumeration."""

    WINTER = "WINTER"
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    FALL = "FALL"


class MediaSource(str, Enum):
    """Media source enumeration."""

    ORIGINAL = "ORIGINAL"
    MANGA = "MANGA"
    LIGHT_NOVEL = "LIGHT_NOVEL"
    VISUAL_NOVEL = "VISUAL_NOVEL"
    VIDEO_GAME = "VIDEO_GAME"
    OTHER = "OTHER"
    NOVEL = "NOVEL"
    DOUJINSHI = "DOUJINSHI"
    ANIME = "ANIME"
    WEB_NOVEL = "WEB_NOVEL"
    LIVE_ACTION = "LIVE_ACTION"
    GAME = "GAME"
    COMIC = "COMIC"
    MULTIMEDIA_PROJECT = "MULTIMEDIA_PROJECT"
    PICTURE_BOOK = "PICTURE_BOOK"


class RelationType(str, Enum):
    """Relation type enumeration."""

    ADAPTATION = "ADAPTATION"
    PREQUEL = "PREQUEL"
    SEQUEL = "SEQUEL"
    PARENT = "PARENT"
    SIDE_STORY = "SIDE_STORY"
    CHARACTER = "CHARACTER"
    SUMMARY = "SUMMARY"
    ALTERNATIVE = "ALTERNATIVE"
    SPIN_OFF = "SPIN_OFF"
    OTHER = "OTHER"
    SOURCE = "SOURCE"
    COMPILATION = "COMPILATION"
    CONTAINS = "CONTAINS"


class CharacterRole(str, Enum):
    """Character role enumeration."""

    MAIN = "MAIN"
    SUPPORTING = "SUPPORTING"
    BACKGROUND = "BACKGROUND"


class StaffLanguage(str, Enum):
    """Staff language enumeration."""

    JAPANESE = "JAPANESE"
    ENGLISH = "ENGLISH"
    KOREAN = "KOREAN"
    ITALIAN = "ITALIAN"
    SPANISH = "SPANISH"
    PORTUGUESE = "PORTUGUESE"
    FRENCH = "FRENCH"
    GERMAN = "GERMAN"
    HEBREW = "HEBREW"
    HUNGARIAN = "HUNGARIAN"


class ExternalLinkType(str, Enum):
    """External link type enumeration."""

    INFO = "INFO"
    STREAMING = "STREAMING"
    SOCIAL = "SOCIAL"


class RankingType(str, Enum):
    """Ranking type enumeration."""

    RATED = "RATED"
    POPULAR = "POPULAR"


class MediaListStatus(str, Enum):
    """Media list status enumeration."""

    CURRENT = "CURRENT"
    PLANNING = "PLANNING"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"
    PAUSED = "PAUSED"
    REPEATING = "REPEATING"


# Base models
class AniListDate(BaseModel):
    """AniList date model."""

    year: int | None = None
    month: int | None = None
    day: int | None = None


class MediaTitle(BaseModel):
    """Media title model."""

    romaji: str | None = None
    english: str | None = None
    native: str | None = None
    userPreferred: str | None = None


class CoverImage(BaseModel):
    """Cover image model."""

    extraLarge: str | None = None
    large: str | None = None
    medium: str | None = None
    color: str | None = None


class Trailer(BaseModel):
    """Trailer model."""

    id: str | None = None
    site: str | None = None
    thumbnail: str | None = None


class NextAiringEpisode(BaseModel):
    """Next airing episode model."""

    airingAt: int | None = None
    timeUntilAiring: int | None = None
    episode: int | None = None


class MediaTag(BaseModel):
    """Media tag model."""

    id: int
    name: str
    description: str | None = None
    category: str | None = None
    rank: int | None = None
    isGeneralSpoiler: bool | None = None
    isMediaSpoiler: bool | None = None
    isAdult: bool | None = None
    userId: int | None = None


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


class StatusDistribution(BaseModel):
    """Status distribution model."""

    status: MediaListStatus | None = None
    amount: int | None = None


class ScoreDistribution(BaseModel):
    """Score distribution model."""

    score: int | None = None
    amount: int | None = None


class MediaStats(BaseModel):
    """Media statistics model."""

    statusDistribution: list[StatusDistribution] | None = None
    scoreDistribution: list[ScoreDistribution] | None = None


class MediaListEntry(BaseModel):
    """Media list entry model."""

    id: int
    status: MediaListStatus | None = None
    score: float | None = None
    progress: int | None = None
    progressVolumes: int | None = None
    repeat: int | None = None
    priority: int | None = None
    private: bool | None = None
    notes: str | None = None
    hiddenFromStatusLists: bool | None = None
    customLists: dict[str, Any] | None = None
    advancedScores: dict[str, Any] | None = None
    startedAt: AniListDate | None = None
    completedAt: AniListDate | None = None
    updatedAt: int | None = None
    createdAt: int | None = None


class StreamingEpisode(BaseModel):
    """Streaming episode model."""

    title: str | None = None
    thumbnail: str | None = None
    url: str | None = None
    site: str | None = None


class ExternalLink(BaseModel):
    """External link model."""

    id: int
    url: str | None = None
    site: str
    siteId: int | None = None
    type: ExternalLinkType | None = None
    language: str | None = None
    color: str | None = None
    icon: str | None = None
    notes: str | None = None
    isDisabled: bool | None = None


# Character and Staff models
class CharacterName(BaseModel):
    """Character name model."""

    first: str | None = None
    middle: str | None = None
    last: str | None = None
    full: str | None = None
    native: str | None = None
    alternative: list[str] | None = None
    alternativeSpoiler: list[str] | None = None
    userPreferred: str | None = None


class CharacterImage(BaseModel):
    """Character image model."""

    large: str | None = None
    medium: str | None = None


class Character(BaseModel):
    """Character model."""

    id: int
    name: CharacterName | None = None
    image: CharacterImage | None = None
    description: str | None = None
    gender: str | None = None
    dateOfBirth: AniListDate | None = None
    age: str | None = None
    bloodType: str | None = None
    isFavourite: bool | None = None
    isFavouriteBlocked: bool | None = None
    siteUrl: str | None = None


class StaffName(BaseModel):
    """Staff name model."""

    first: str | None = None
    middle: str | None = None
    last: str | None = None
    full: str | None = None
    native: str | None = None
    alternative: list[str] | None = None
    userPreferred: str | None = None


class StaffImage(BaseModel):
    """Staff image model."""

    large: str | None = None
    medium: str | None = None


class Staff(BaseModel):
    """Staff model."""

    id: int
    name: StaffName | None = None
    languageV2: str | None = None
    image: StaffImage | None = None
    description: str | None = None
    primaryOccupations: list[str] | None = None
    gender: str | None = None
    dateOfBirth: AniListDate | None = None
    dateOfDeath: AniListDate | None = None
    age: int | None = None
    yearsActive: list[int] | None = None
    homeTown: str | None = None
    bloodType: str | None = None
    isFavourite: bool | None = None
    isFavouriteBlocked: bool | None = None
    siteUrl: str | None = None


class VoiceActor(BaseModel):
    """Voice actor model."""

    id: int
    name: StaffName | None = None
    language: str | None = None
    languageV2: str | None = None
    image: StaffImage | None = None
    description: str | None = None
    primaryOccupations: list[str] | None = None
    gender: str | None = None
    dateOfBirth: AniListDate | None = None
    dateOfDeath: AniListDate | None = None
    age: int | None = None
    yearsActive: list[int] | None = None
    homeTown: str | None = None
    bloodType: str | None = None
    isFavourite: bool | None = None
    isFavouriteBlocked: bool | None = None
    siteUrl: str | None = None


class CharacterEdge(BaseModel):
    """Character edge model."""

    id: int | None = None
    role: CharacterRole | None = None
    name: str | None = None
    voiceActors: list[VoiceActor] | None = None
    node: Character | None = None


class StaffEdge(BaseModel):
    """Staff edge model."""

    id: int | None = None
    role: str | None = None
    node: Staff | None = None


class CharacterConnection(BaseModel):
    """Character connection model."""

    edges: list[CharacterEdge] | None = None
    nodes: list[Character] | None = None


class StaffConnection(BaseModel):
    """Staff connection model."""

    edges: list[StaffEdge] | None = None
    nodes: list[Staff] | None = None


# Studio models
class Studio(BaseModel):
    """Studio model."""

    id: int
    name: str
    isAnimationStudio: bool | None = None
    siteUrl: str | None = None
    isFavourite: bool | None = None


class StudioEdge(BaseModel):
    """Studio edge model."""

    id: int | None = None
    isMain: bool
    node: Studio | None = None


class StudioConnection(BaseModel):
    """Studio connection model."""

    edges: list[StudioEdge] | None = None
    nodes: list[Studio] | None = None


# User and Review models
class UserAvatar(BaseModel):
    """User avatar model."""

    large: str | None = None
    medium: str | None = None


class User(BaseModel):
    """User model."""

    id: int
    name: str
    avatar: UserAvatar | None = None
    bannerImage: str | None = None
    about: str | None = None
    isFollowing: bool | None = None
    isFollower: bool | None = None
    isBlocked: bool | None = None
    bans: list[Any] | None = None
    options: dict[str, Any] | None = None
    mediaListOptions: dict[str, Any] | None = None
    favourites: dict[str, Any] | None = None
    statistics: dict[str, Any] | None = None
    unreadNotificationCount: int | None = None
    siteUrl: str | None = None
    donatorTier: int | None = None
    donatorBadge: str | None = None
    moderatorRoles: list[str] | None = None
    createdAt: int | None = None
    updatedAt: int | None = None


class Review(BaseModel):
    """Review model."""

    id: int
    userId: int | None = None
    mediaId: int | None = None
    mediaType: MediaType | None = None
    summary: str | None = None
    body: str | None = None
    rating: int | None = None
    ratingAmount: int | None = None
    userRating: int | None = None
    score: int | None = None
    private: bool | None = None
    siteUrl: str | None = None
    createdAt: int | None = None
    updatedAt: int | None = None
    user: User | None = None


class PageInfo(BaseModel):
    """Page info model."""

    total: int | None = None
    perPage: int | None = None
    currentPage: int | None = None
    lastPage: int | None = None
    hasNextPage: bool | None = None


class ReviewConnection(BaseModel):
    """Review connection model."""

    edges: list[Any] | None = None
    nodes: list[Review] | None = None
    pageInfo: PageInfo | None = None


# Recommendation models
class MediaRecommendation(BaseModel):
    """Media recommendation model."""

    id: int
    title: MediaTitle | None = None
    format: MediaFormat | None = None
    type: MediaType | None = None
    status: MediaStatus | None = None
    bannerImage: str | None = None
    coverImage: CoverImage | None = None
    siteUrl: str | None = None


class Recommendation(BaseModel):
    """Recommendation model."""

    id: int
    rating: int | None = None
    userRating: int | str | None = None
    mediaRecommendation: MediaRecommendation | None = None
    user: User | None = None

    @field_validator("userRating", mode="before")
    @classmethod
    def validate_user_rating(cls, v):
        """Convert NO_RATING string to None."""
        if v == "NO_RATING":
            return None
        return v


class RecommendationConnection(BaseModel):
    """Recommendation connection model."""

    edges: list[Any] | None = None
    nodes: list[Recommendation] | None = None
    pageInfo: PageInfo | None = None


# Media relation models
class MediaEdge(BaseModel):
    """Media edge model."""

    id: int | None = None
    relationType: RelationType | None = None
    isMainStudio: bool | None = None
    characters: list[Character] | None = None
    characterRole: CharacterRole | None = None
    characterName: str | None = None
    roleNotes: str | None = None
    dubGroup: str | None = None
    staffRole: str | None = None
    voiceActors: list[VoiceActor] | None = None
    voiceActorRoles: list[Any] | None = None
    node: Media | None = None


class MediaConnection(BaseModel):
    """Media connection model."""

    edges: list[MediaEdge] | None = None
    nodes: list[Media] | None = None
    pageInfo: PageInfo | None = None


# Forward declare Media for use in other models
class Media(BaseModel):
    """Main media model."""

    id: int
    idMal: int | None = None
    title: MediaTitle | None = None
    type: MediaType | None = None
    format: MediaFormat | None = None
    status: MediaStatus | None = None
    description: str | None = None
    startDate: AniListDate | None = None
    endDate: AniListDate | None = None
    season: MediaSeason | None = None
    seasonYear: int | None = None
    seasonInt: int | None = None
    episodes: int | None = None
    duration: int | None = None
    chapters: int | None = None
    volumes: int | None = None
    countryOfOrigin: str | None = None
    isLicensed: bool | None = None
    source: MediaSource | None = None
    hashtag: str | None = None
    trailer: Trailer | None = None
    updatedAt: int | None = None
    coverImage: CoverImage | None = None
    bannerImage: str | None = None
    genres: list[str] | None = None
    synonyms: list[str] | None = None
    averageScore: int | None = None
    meanScore: int | None = None
    popularity: int | None = None
    isLocked: bool | None = None
    trending: int | None = None
    favourites: int | None = None
    tags: list[MediaTag] | None = None
    relations: MediaConnection | None = None
    characters: CharacterConnection | None = None
    characterPreview: CharacterConnection | None = None
    staff: StaffConnection | None = None
    staffPreview: StaffConnection | None = None
    studios: StudioConnection | None = None
    isFavourite: bool | None = None
    isFavouriteBlocked: bool | None = None
    isAdult: bool | None = None
    nextAiringEpisode: NextAiringEpisode | None = None
    airingSchedule: Any | None = None
    trends: Any | None = None
    externalLinks: list[ExternalLink] | None = None
    streamingEpisodes: list[StreamingEpisode] | None = None
    rankings: list[MediaRanking] | None = None
    mediaListEntry: MediaListEntry | None = None
    reviews: ReviewConnection | None = None
    reviewPreview: ReviewConnection | None = None
    recommendations: RecommendationConnection | None = None
    stats: MediaStats | None = None
    siteUrl: str | None = None
    autoCreateForumThread: bool | None = None
    isRecommendationBlocked: bool | None = None
    isReviewBlocked: bool | None = None
    modNotes: str | None = None


# Response models
class MediaResponse(BaseModel):
    """Response model for single media query."""

    media: Media | None = None


class PageResponse(BaseModel):
    """Response model for paginated media query."""

    pageInfo: PageInfo | None = None
    media: list[Media] | None = None


class MediaPageResponse(BaseModel):
    """Response model for media page query."""

    Page: PageResponse | None = None


# Search and query models
class MediaSearchVariables(BaseModel):
    """Variables for media search query."""

    search: str | None = None
    type: MediaType | None = None
    format: list[MediaFormat] | None = None
    status: MediaStatus | None = None
    season: MediaSeason | None = None
    seasonYear: int | None = None
    year: str | None = None
    onList: bool | None = None
    isAdult: bool | None = False
    genre: list[str] | None = None
    tag: list[str] | None = None
    page: int | None = 1
    perPage: int | None = 10


class MediaByIdVariables(BaseModel):
    """Variables for media by ID query."""

    id: int
    type: MediaType | None = None


# Update forward references
Media.model_rebuild()
MediaEdge.model_rebuild()
MediaConnection.model_rebuild()
MediaResponse.model_rebuild()
PageResponse.model_rebuild()
MediaPageResponse.model_rebuild()
