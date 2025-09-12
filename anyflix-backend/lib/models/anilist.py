"""AniList API models for GraphQL responses."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


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

    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


class MediaTitle(BaseModel):
    """Media title model."""

    romaji: Optional[str] = None
    english: Optional[str] = None
    native: Optional[str] = None
    userPreferred: Optional[str] = None


class CoverImage(BaseModel):
    """Cover image model."""

    extraLarge: Optional[str] = None
    large: Optional[str] = None
    medium: Optional[str] = None
    color: Optional[str] = None


class Trailer(BaseModel):
    """Trailer model."""

    id: Optional[str] = None
    site: Optional[str] = None
    thumbnail: Optional[str] = None


class NextAiringEpisode(BaseModel):
    """Next airing episode model."""

    airingAt: Optional[int] = None
    timeUntilAiring: Optional[int] = None
    episode: Optional[int] = None


class MediaTag(BaseModel):
    """Media tag model."""

    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    rank: Optional[int] = None
    isGeneralSpoiler: Optional[bool] = None
    isMediaSpoiler: Optional[bool] = None
    isAdult: Optional[bool] = None
    userId: Optional[int] = None


class MediaRanking(BaseModel):
    """Media ranking model."""

    id: int
    rank: int
    type: RankingType
    format: MediaFormat
    year: Optional[int] = None
    season: Optional[MediaSeason] = None
    allTime: Optional[bool] = None
    context: str


class StatusDistribution(BaseModel):
    """Status distribution model."""

    status: Optional[MediaListStatus] = None
    amount: Optional[int] = None


class ScoreDistribution(BaseModel):
    """Score distribution model."""

    score: Optional[int] = None
    amount: Optional[int] = None


class MediaStats(BaseModel):
    """Media statistics model."""

    statusDistribution: Optional[List[StatusDistribution]] = None
    scoreDistribution: Optional[List[ScoreDistribution]] = None


class MediaListEntry(BaseModel):
    """Media list entry model."""

    id: int
    status: Optional[MediaListStatus] = None
    score: Optional[float] = None
    progress: Optional[int] = None
    progressVolumes: Optional[int] = None
    repeat: Optional[int] = None
    priority: Optional[int] = None
    private: Optional[bool] = None
    notes: Optional[str] = None
    hiddenFromStatusLists: Optional[bool] = None
    customLists: Optional[Dict[str, Any]] = None
    advancedScores: Optional[Dict[str, Any]] = None
    startedAt: Optional[AniListDate] = None
    completedAt: Optional[AniListDate] = None
    updatedAt: Optional[int] = None
    createdAt: Optional[int] = None


class StreamingEpisode(BaseModel):
    """Streaming episode model."""

    title: Optional[str] = None
    thumbnail: Optional[str] = None
    url: Optional[str] = None
    site: Optional[str] = None


class ExternalLink(BaseModel):
    """External link model."""

    id: int
    url: Optional[str] = None
    site: str
    siteId: Optional[int] = None
    type: Optional[ExternalLinkType] = None
    language: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    notes: Optional[str] = None
    isDisabled: Optional[bool] = None


# Character and Staff models
class CharacterName(BaseModel):
    """Character name model."""

    first: Optional[str] = None
    middle: Optional[str] = None
    last: Optional[str] = None
    full: Optional[str] = None
    native: Optional[str] = None
    alternative: Optional[List[str]] = None
    alternativeSpoiler: Optional[List[str]] = None
    userPreferred: Optional[str] = None


class CharacterImage(BaseModel):
    """Character image model."""

    large: Optional[str] = None
    medium: Optional[str] = None


class Character(BaseModel):
    """Character model."""

    id: int
    name: Optional[CharacterName] = None
    image: Optional[CharacterImage] = None
    description: Optional[str] = None
    gender: Optional[str] = None
    dateOfBirth: Optional[AniListDate] = None
    age: Optional[str] = None
    bloodType: Optional[str] = None
    isFavourite: Optional[bool] = None
    isFavouriteBlocked: Optional[bool] = None
    siteUrl: Optional[str] = None


class StaffName(BaseModel):
    """Staff name model."""

    first: Optional[str] = None
    middle: Optional[str] = None
    last: Optional[str] = None
    full: Optional[str] = None
    native: Optional[str] = None
    alternative: Optional[List[str]] = None
    userPreferred: Optional[str] = None


class StaffImage(BaseModel):
    """Staff image model."""

    large: Optional[str] = None
    medium: Optional[str] = None


class Staff(BaseModel):
    """Staff model."""

    id: int
    name: Optional[StaffName] = None
    languageV2: Optional[str] = None
    image: Optional[StaffImage] = None
    description: Optional[str] = None
    primaryOccupations: Optional[List[str]] = None
    gender: Optional[str] = None
    dateOfBirth: Optional[AniListDate] = None
    dateOfDeath: Optional[AniListDate] = None
    age: Optional[int] = None
    yearsActive: Optional[List[int]] = None
    homeTown: Optional[str] = None
    bloodType: Optional[str] = None
    isFavourite: Optional[bool] = None
    isFavouriteBlocked: Optional[bool] = None
    siteUrl: Optional[str] = None


class VoiceActor(BaseModel):
    """Voice actor model."""

    id: int
    name: Optional[StaffName] = None
    language: Optional[str] = None
    languageV2: Optional[str] = None
    image: Optional[StaffImage] = None
    description: Optional[str] = None
    primaryOccupations: Optional[List[str]] = None
    gender: Optional[str] = None
    dateOfBirth: Optional[AniListDate] = None
    dateOfDeath: Optional[AniListDate] = None
    age: Optional[int] = None
    yearsActive: Optional[List[int]] = None
    homeTown: Optional[str] = None
    bloodType: Optional[str] = None
    isFavourite: Optional[bool] = None
    isFavouriteBlocked: Optional[bool] = None
    siteUrl: Optional[str] = None


class CharacterEdge(BaseModel):
    """Character edge model."""

    id: Optional[int] = None
    role: Optional[CharacterRole] = None
    name: Optional[str] = None
    voiceActors: Optional[List[VoiceActor]] = None
    node: Optional[Character] = None


class StaffEdge(BaseModel):
    """Staff edge model."""

    id: Optional[int] = None
    role: Optional[str] = None
    node: Optional[Staff] = None


class CharacterConnection(BaseModel):
    """Character connection model."""

    edges: Optional[List[CharacterEdge]] = None
    nodes: Optional[List[Character]] = None


class StaffConnection(BaseModel):
    """Staff connection model."""

    edges: Optional[List[StaffEdge]] = None
    nodes: Optional[List[Staff]] = None


# Studio models
class Studio(BaseModel):
    """Studio model."""

    id: int
    name: str
    isAnimationStudio: Optional[bool] = None
    siteUrl: Optional[str] = None
    isFavourite: Optional[bool] = None


class StudioEdge(BaseModel):
    """Studio edge model."""

    id: Optional[int] = None
    isMain: bool
    node: Optional[Studio] = None


class StudioConnection(BaseModel):
    """Studio connection model."""

    edges: Optional[List[StudioEdge]] = None
    nodes: Optional[List[Studio]] = None


# User and Review models
class UserAvatar(BaseModel):
    """User avatar model."""

    large: Optional[str] = None
    medium: Optional[str] = None


class User(BaseModel):
    """User model."""

    id: int
    name: str
    avatar: Optional[UserAvatar] = None
    bannerImage: Optional[str] = None
    about: Optional[str] = None
    isFollowing: Optional[bool] = None
    isFollower: Optional[bool] = None
    isBlocked: Optional[bool] = None
    bans: Optional[List[Any]] = None
    options: Optional[Dict[str, Any]] = None
    mediaListOptions: Optional[Dict[str, Any]] = None
    favourites: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    unreadNotificationCount: Optional[int] = None
    siteUrl: Optional[str] = None
    donatorTier: Optional[int] = None
    donatorBadge: Optional[str] = None
    moderatorRoles: Optional[List[str]] = None
    createdAt: Optional[int] = None
    updatedAt: Optional[int] = None


class Review(BaseModel):
    """Review model."""

    id: int
    userId: Optional[int] = None
    mediaId: Optional[int] = None
    mediaType: Optional[MediaType] = None
    summary: Optional[str] = None
    body: Optional[str] = None
    rating: Optional[int] = None
    ratingAmount: Optional[int] = None
    userRating: Optional[int] = None
    score: Optional[int] = None
    private: Optional[bool] = None
    siteUrl: Optional[str] = None
    createdAt: Optional[int] = None
    updatedAt: Optional[int] = None
    user: Optional[User] = None


class PageInfo(BaseModel):
    """Page info model."""

    total: Optional[int] = None
    perPage: Optional[int] = None
    currentPage: Optional[int] = None
    lastPage: Optional[int] = None
    hasNextPage: Optional[bool] = None


class ReviewConnection(BaseModel):
    """Review connection model."""

    edges: Optional[List[Any]] = None
    nodes: Optional[List[Review]] = None
    pageInfo: Optional[PageInfo] = None


# Recommendation models
class MediaRecommendation(BaseModel):
    """Media recommendation model."""

    id: int
    title: Optional[MediaTitle] = None
    format: Optional[MediaFormat] = None
    type: Optional[MediaType] = None
    status: Optional[MediaStatus] = None
    bannerImage: Optional[str] = None
    coverImage: Optional[CoverImage] = None
    siteUrl: Optional[str] = None


class Recommendation(BaseModel):
    """Recommendation model."""

    id: int
    rating: Optional[int] = None
    userRating: Optional[Union[int, str]] = None
    mediaRecommendation: Optional[MediaRecommendation] = None
    user: Optional[User] = None

    @field_validator("userRating", mode="before")
    @classmethod
    def validate_user_rating(cls, v):
        """Convert NO_RATING string to None."""
        if v == "NO_RATING":
            return None
        return v


class RecommendationConnection(BaseModel):
    """Recommendation connection model."""

    edges: Optional[List[Any]] = None
    nodes: Optional[List[Recommendation]] = None
    pageInfo: Optional[PageInfo] = None


# Media relation models
class MediaEdge(BaseModel):
    """Media edge model."""

    id: Optional[int] = None
    relationType: Optional[RelationType] = None
    isMainStudio: Optional[bool] = None
    characters: Optional[List[Character]] = None
    characterRole: Optional[CharacterRole] = None
    characterName: Optional[str] = None
    roleNotes: Optional[str] = None
    dubGroup: Optional[str] = None
    staffRole: Optional[str] = None
    voiceActors: Optional[List[VoiceActor]] = None
    voiceActorRoles: Optional[List[Any]] = None
    node: Optional[Media] = None


class MediaConnection(BaseModel):
    """Media connection model."""

    edges: Optional[List[MediaEdge]] = None
    nodes: Optional[List[Media]] = None
    pageInfo: Optional[PageInfo] = None


# Forward declare Media for use in other models
class Media(BaseModel):
    """Main media model."""

    id: int
    idMal: Optional[int] = None
    title: Optional[MediaTitle] = None
    type: Optional[MediaType] = None
    format: Optional[MediaFormat] = None
    status: Optional[MediaStatus] = None
    description: Optional[str] = None
    startDate: Optional[AniListDate] = None
    endDate: Optional[AniListDate] = None
    season: Optional[MediaSeason] = None
    seasonYear: Optional[int] = None
    seasonInt: Optional[int] = None
    episodes: Optional[int] = None
    duration: Optional[int] = None
    chapters: Optional[int] = None
    volumes: Optional[int] = None
    countryOfOrigin: Optional[str] = None
    isLicensed: Optional[bool] = None
    source: Optional[MediaSource] = None
    hashtag: Optional[str] = None
    trailer: Optional[Trailer] = None
    updatedAt: Optional[int] = None
    coverImage: Optional[CoverImage] = None
    bannerImage: Optional[str] = None
    genres: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    averageScore: Optional[int] = None
    meanScore: Optional[int] = None
    popularity: Optional[int] = None
    isLocked: Optional[bool] = None
    trending: Optional[int] = None
    favourites: Optional[int] = None
    tags: Optional[List[MediaTag]] = None
    relations: Optional[MediaConnection] = None
    characters: Optional[CharacterConnection] = None
    characterPreview: Optional[CharacterConnection] = None
    staff: Optional[StaffConnection] = None
    staffPreview: Optional[StaffConnection] = None
    studios: Optional[StudioConnection] = None
    isFavourite: Optional[bool] = None
    isFavouriteBlocked: Optional[bool] = None
    isAdult: Optional[bool] = None
    nextAiringEpisode: Optional[NextAiringEpisode] = None
    airingSchedule: Optional[Any] = None
    trends: Optional[Any] = None
    externalLinks: Optional[List[ExternalLink]] = None
    streamingEpisodes: Optional[List[StreamingEpisode]] = None
    rankings: Optional[List[MediaRanking]] = None
    mediaListEntry: Optional[MediaListEntry] = None
    reviews: Optional[ReviewConnection] = None
    reviewPreview: Optional[ReviewConnection] = None
    recommendations: Optional[RecommendationConnection] = None
    stats: Optional[MediaStats] = None
    siteUrl: Optional[str] = None
    autoCreateForumThread: Optional[bool] = None
    isRecommendationBlocked: Optional[bool] = None
    isReviewBlocked: Optional[bool] = None
    modNotes: Optional[str] = None


# Response models
class MediaResponse(BaseModel):
    """Response model for single media query."""

    media: Optional[Media] = None


class PageResponse(BaseModel):
    """Response model for paginated media query."""

    pageInfo: Optional[PageInfo] = None
    media: Optional[List[Media]] = None


class MediaPageResponse(BaseModel):
    """Response model for media page query."""

    Page: Optional[PageResponse] = None


# Search and query models
class MediaSearchVariables(BaseModel):
    """Variables for media search query."""

    search: Optional[str] = None
    type: Optional[MediaType] = None
    format: Optional[List[MediaFormat]] = None
    status: Optional[MediaStatus] = None
    season: Optional[MediaSeason] = None
    seasonYear: Optional[int] = None
    year: Optional[str] = None
    onList: Optional[bool] = None
    isAdult: Optional[bool] = False
    genre: Optional[List[str]] = None
    tag: Optional[List[str]] = None
    sort: Optional[List[str]] = None
    page: Optional[int] = 1
    perPage: Optional[int] = 20


class MediaByIdVariables(BaseModel):
    """Variables for media by ID query."""

    id: int
    type: Optional[MediaType] = None


# Update forward references
Media.model_rebuild()
MediaEdge.model_rebuild()
MediaConnection.model_rebuild()
MediaResponse.model_rebuild()
PageResponse.model_rebuild()
MediaPageResponse.model_rebuild()
