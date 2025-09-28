"""TMDB (The Movie Database) models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TMDBGenre(BaseModel):
    """TMDB genre model."""

    id: int
    name: str


class TMDBProductionCompany(BaseModel):
    """TMDB production company model."""

    id: int
    logo_path: str | None = None
    name: str
    origin_country: str


class TMDBProductionCountry(BaseModel):
    """TMDB production country model."""

    iso_3166_1: str
    name: str


class TMDBSpokenLanguage(BaseModel):
    """TMDB spoken language model."""

    english_name: str
    iso_639_1: str
    name: str


class TMDBVideoType(str, Enum):
    """TMDB video type enumeration."""

    TRAILER = "Trailer"
    CLIP = "Clip"
    TEASER = "Teaser"
    OPENING_CREDITS = "Opening Credits"
    ENDING_CREDITS = "Ending Credits"


class TMDBVideoSite(str, Enum):
    """TMDB video site enumeration."""

    YOUTUBE = "YouTube"


class TMDBVideo(BaseModel):
    """TMDB video model."""

    iso_639_1: str
    iso_3166_1: str
    name: str
    key: str
    site: str | TMDBVideoSite
    size: int
    type: TMDBVideoType | str | None = None
    official: bool
    published_at: str
    id: str


class TMDBVideoResult(BaseModel):
    """TMDB video result model."""

    results: list[TMDBVideo] = Field(default_factory=list)


class TMDBImage(BaseModel):
    """TMDB image model."""

    aspect_ratio: float
    height: int
    iso_639_1: str | None = None
    file_path: str
    vote_average: float
    vote_count: int
    width: int


class TMDBImages(BaseModel):
    """TMDB images collection."""

    backdrops: list[TMDBImage] = Field(default_factory=list)
    logos: list[TMDBImage] = Field(default_factory=list)
    posters: list[TMDBImage] = Field(default_factory=list)


class TMDBExternalIds(BaseModel):
    """TMDB external IDs."""

    imdb_id: str | None = None
    freebase_mid: str | None = None
    freebase_id: str | None = None
    tvdb_id: int | None = None
    tvrage_id: int | None = None
    wikidata_id: str | None = None
    facebook_id: str | None = None
    instagram_id: str | None = None
    twitter_id: str | None = None


class TMDBCreatedBy(BaseModel):
    """TMDB created by person."""

    id: int
    credit_id: str
    name: str
    gender: int
    profile_path: str | None = None


class TMDBNetwork(BaseModel):
    """TMDB network model."""

    id: int
    logo_path: str | None = None
    name: str
    origin_country: str


class TMDBSeason(BaseModel):
    """TMDB season model."""

    air_date: str | None = None
    episode_count: int
    id: int
    name: str
    overview: str
    poster_path: str | None = None
    season_number: int
    vote_average: float


class TMDBEpisode(BaseModel):
    """TMDB episode model."""

    id: int
    name: str
    overview: str
    vote_average: float
    vote_count: int
    air_date: str | None = None
    episode_number: int
    episode_type: str
    production_code: str
    runtime: int | None = None
    season_number: int
    show_id: int
    still_path: str | None = None


class TMDBMovieDetail(BaseModel):
    """TMDB movie detail model."""

    adult: bool
    backdrop_path: str | None = None
    belongs_to_collection: dict[str, Any] | None = None
    budget: int
    genres: list[TMDBGenre] = Field(default_factory=list)
    homepage: str | None = None
    id: int
    imdb_id: str | None = None
    original_language: str
    original_title: str
    overview: str | None = None
    popularity: float
    poster_path: str | None = None
    production_companies: list[TMDBProductionCompany] = Field(default_factory=list)
    production_countries: list[TMDBProductionCountry] = Field(default_factory=list)
    release_date: str | None = None
    revenue: int
    runtime: int | None = None
    spoken_languages: list[TMDBSpokenLanguage] = Field(default_factory=list)
    status: str
    tagline: str | None = None
    title: str
    video: bool
    vote_average: float
    vote_count: int

    # Additional fields when requested
    videos: TMDBVideoResult | None = None
    images: TMDBImages | None = None
    external_ids: TMDBExternalIds | None = None


class TMDBTVDetail(BaseModel):
    """TMDB TV show detail model."""

    adult: bool
    backdrop_path: str | None = None
    created_by: list[TMDBCreatedBy] = Field(default_factory=list)
    episode_run_time: list[int] = Field(default_factory=list)
    first_air_date: str | None = None
    genres: list[TMDBGenre] = Field(default_factory=list)
    homepage: str
    id: int
    in_production: bool
    languages: list[str] = Field(default_factory=list)
    last_air_date: str | None = None
    last_episode_to_air: TMDBEpisode | None = None
    name: str
    networks: list[TMDBNetwork] = Field(default_factory=list)
    next_episode_to_air: TMDBEpisode | None = None
    number_of_episodes: int
    number_of_seasons: int
    origin_country: list[str] = Field(default_factory=list)
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: str | None = None
    production_companies: list[TMDBProductionCompany] = Field(default_factory=list)
    production_countries: list[TMDBProductionCountry] = Field(default_factory=list)
    seasons: list[TMDBSeason] = Field(default_factory=list)
    spoken_languages: list[TMDBSpokenLanguage] = Field(default_factory=list)
    status: str
    tagline: str
    type: str
    vote_average: float
    vote_count: int

    # Additional fields when requested
    videos: TMDBVideoResult | None = None
    images: TMDBImages | None = None
    external_ids: TMDBExternalIds | None = None


class TMDBSearchResult(BaseModel):
    """TMDB search result model."""

    id: int
    media_type: str  # "movie", "tv", or "person"
    adult: bool | None = None
    backdrop_path: str | None = None
    poster_path: str | None = None
    popularity: float = 0.0
    vote_average: float | None = None
    vote_count: int | None = None
    overview: str | None = None
    genre_ids: list[int] = Field(default_factory=list)
    original_language: str | None = None

    # Movie specific fields
    title: str | None = None
    original_title: str | None = None
    release_date: str | None = None
    video: bool | None = None

    # TV specific fields
    name: str | None = None
    original_name: str | None = None
    first_air_date: str | None = None
    origin_country: list[str] = Field(default_factory=list)

    # Person specific fields (for when media_type is "person")
    profile_path: str | None = None
    known_for: list[dict[str, Any]] = Field(default_factory=list)
    known_for_department: str | None = None
    gender: int | None = None


class TMDBSearchResponse(BaseModel):
    """TMDB search response model."""

    page: int
    results: list[TMDBSearchResult] = Field(default_factory=list)
    total_pages: int
    total_results: int


class TMDBConfiguration(BaseModel):
    """TMDB configuration model."""

    images: dict[str, Any]
    change_keys: list[str] = Field(default_factory=list)


# TMDB Movie Genres
TMDB_MOVIE_GENRES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}

# TMDB TV Genres
TMDB_TV_GENRES = {
    10759: "Action & Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    10762: "Kids",
    9648: "Mystery",
    10763: "News",
    10764: "Reality",
    10765: "Sci-Fi & Fantasy",
    10766: "Soap",
    10767: "Talk",
    10768: "War & Politics",
    37: "Western",
}

# Combined genre mapping for comprehensive lookup
TMDB_ALL_GENRES = {
    **TMDB_MOVIE_GENRES,
    **TMDB_TV_GENRES,
}


def get_genre_name(genre_id: int, media_type: str = "all") -> str | None:
    """
    Get genre name by ID.

    Args:
        genre_id: The TMDB genre ID
        media_type: Type of media ("movie", "tv", or "all")

    Returns:
        Genre name if found, None otherwise
    """
    if media_type == "movie":
        return TMDB_MOVIE_GENRES.get(genre_id)
    if media_type == "tv":
        return TMDB_TV_GENRES.get(genre_id)
    return TMDB_ALL_GENRES.get(genre_id)


def get_genres_by_ids(genre_ids: list[int], media_type: str = "all") -> list[str]:
    """
    Get genre names by list of IDs.

    Args:
        genre_ids: List of TMDB genre IDs
        media_type: Type of media ("movie", "tv", or "all")

    Returns:
        List of genre names (excludes None values)
    """
    genres = []
    for genre_id in genre_ids:
        genre_name = get_genre_name(genre_id, media_type)
        if genre_name:
            genres.append(genre_name.lower())
    return genres


def find_genre_id(genre_name: str, media_type: str = "all") -> int | None:
    """
    Find genre ID by name (case-insensitive).

    Args:
        genre_name: The genre name to search for
        media_type: Type of media ("movie", "tv", or "all")

    Returns:
        Genre ID if found, None otherwise
    """
    genre_name_lower = genre_name.lower()

    search_dict = TMDB_ALL_GENRES
    if media_type == "movie":
        search_dict = TMDB_MOVIE_GENRES
    elif media_type == "tv":
        search_dict = TMDB_TV_GENRES

    for genre_id, name in search_dict.items():
        if name.lower() == genre_name_lower:
            return genre_id

    return None
