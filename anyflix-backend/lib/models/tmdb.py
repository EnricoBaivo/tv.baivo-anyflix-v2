"""TMDB (The Movie Database) models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TMDBGenre(BaseModel):
    """TMDB genre model."""

    id: int
    name: str


class TMDBProductionCompany(BaseModel):
    """TMDB production company model."""

    id: int
    logo_path: Optional[str] = None
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


class TMDBVideo(BaseModel):
    """TMDB video model."""

    iso_639_1: str
    iso_3166_1: str
    name: str
    key: str
    site: str
    size: int
    type: str
    official: bool
    published_at: str
    id: str


class TMDBImage(BaseModel):
    """TMDB image model."""

    aspect_ratio: float
    height: int
    iso_639_1: Optional[str] = None
    file_path: str
    vote_average: float
    vote_count: int
    width: int


class TMDBImages(BaseModel):
    """TMDB images collection."""

    backdrops: List[TMDBImage] = Field(default_factory=list)
    logos: List[TMDBImage] = Field(default_factory=list)
    posters: List[TMDBImage] = Field(default_factory=list)


class TMDBExternalIds(BaseModel):
    """TMDB external IDs."""

    imdb_id: Optional[str] = None
    freebase_mid: Optional[str] = None
    freebase_id: Optional[str] = None
    tvdb_id: Optional[int] = None
    tvrage_id: Optional[int] = None
    wikidata_id: Optional[str] = None
    facebook_id: Optional[str] = None
    instagram_id: Optional[str] = None
    twitter_id: Optional[str] = None


class TMDBCreatedBy(BaseModel):
    """TMDB created by person."""

    id: int
    credit_id: str
    name: str
    gender: int
    profile_path: Optional[str] = None


class TMDBNetwork(BaseModel):
    """TMDB network model."""

    id: int
    logo_path: Optional[str] = None
    name: str
    origin_country: str


class TMDBSeason(BaseModel):
    """TMDB season model."""

    air_date: Optional[str] = None
    episode_count: int
    id: int
    name: str
    overview: str
    poster_path: Optional[str] = None
    season_number: int
    vote_average: float


class TMDBEpisode(BaseModel):
    """TMDB episode model."""

    id: int
    name: str
    overview: str
    vote_average: float
    vote_count: int
    air_date: Optional[str] = None
    episode_number: int
    episode_type: str
    production_code: str
    runtime: Optional[int] = None
    season_number: int
    show_id: int
    still_path: Optional[str] = None


class TMDBMovieDetail(BaseModel):
    """TMDB movie detail model."""

    adult: bool
    backdrop_path: Optional[str] = None
    belongs_to_collection: Optional[Dict[str, Any]] = None
    budget: int
    genres: List[TMDBGenre] = Field(default_factory=list)
    homepage: Optional[str] = None
    id: int
    imdb_id: Optional[str] = None
    original_language: str
    original_title: str
    overview: Optional[str] = None
    popularity: float
    poster_path: Optional[str] = None
    production_companies: List[TMDBProductionCompany] = Field(default_factory=list)
    production_countries: List[TMDBProductionCountry] = Field(default_factory=list)
    release_date: Optional[str] = None
    revenue: int
    runtime: Optional[int] = None
    spoken_languages: List[TMDBSpokenLanguage] = Field(default_factory=list)
    status: str
    tagline: Optional[str] = None
    title: str
    video: bool
    vote_average: float
    vote_count: int

    # Additional fields when requested
    videos: Optional[Dict[str, List[TMDBVideo]]] = None
    images: Optional[TMDBImages] = None
    external_ids: Optional[TMDBExternalIds] = None


class TMDBTVDetail(BaseModel):
    """TMDB TV show detail model."""

    adult: bool
    backdrop_path: Optional[str] = None
    created_by: List[TMDBCreatedBy] = Field(default_factory=list)
    episode_run_time: List[int] = Field(default_factory=list)
    first_air_date: Optional[str] = None
    genres: List[TMDBGenre] = Field(default_factory=list)
    homepage: str
    id: int
    in_production: bool
    languages: List[str] = Field(default_factory=list)
    last_air_date: Optional[str] = None
    last_episode_to_air: Optional[TMDBEpisode] = None
    name: str
    networks: List[TMDBNetwork] = Field(default_factory=list)
    next_episode_to_air: Optional[TMDBEpisode] = None
    number_of_episodes: int
    number_of_seasons: int
    origin_country: List[str] = Field(default_factory=list)
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: Optional[str] = None
    production_companies: List[TMDBProductionCompany] = Field(default_factory=list)
    production_countries: List[TMDBProductionCountry] = Field(default_factory=list)
    seasons: List[TMDBSeason] = Field(default_factory=list)
    spoken_languages: List[TMDBSpokenLanguage] = Field(default_factory=list)
    status: str
    tagline: str
    type: str
    vote_average: float
    vote_count: int

    # Additional fields when requested
    videos: Optional[Dict[str, List[TMDBVideo]]] = None
    images: Optional[TMDBImages] = None
    external_ids: Optional[TMDBExternalIds] = None


class TMDBSearchResult(BaseModel):
    """TMDB search result model."""

    id: int
    media_type: str  # "movie", "tv", or "person"
    adult: Optional[bool] = None
    backdrop_path: Optional[str] = None
    poster_path: Optional[str] = None
    popularity: float = 0.0
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    overview: Optional[str] = None
    genre_ids: List[int] = Field(default_factory=list)
    original_language: Optional[str] = None

    # Movie specific fields
    title: Optional[str] = None
    original_title: Optional[str] = None
    release_date: Optional[str] = None
    video: Optional[bool] = None

    # TV specific fields
    name: Optional[str] = None
    original_name: Optional[str] = None
    first_air_date: Optional[str] = None
    origin_country: List[str] = Field(default_factory=list)

    # Person specific fields (for when media_type is "person")
    profile_path: Optional[str] = None
    known_for: List[Dict[str, Any]] = Field(default_factory=list)
    known_for_department: Optional[str] = None
    gender: Optional[int] = None


class TMDBSearchResponse(BaseModel):
    """TMDB search response model."""

    page: int
    results: List[TMDBSearchResult] = Field(default_factory=list)
    total_pages: int
    total_results: int


class TMDBConfiguration(BaseModel):
    """TMDB configuration model."""

    images: Dict[str, Any]
    change_keys: List[str] = Field(default_factory=list)
