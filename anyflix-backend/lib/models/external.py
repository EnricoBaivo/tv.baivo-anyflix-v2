"""External service data models for better OpenAPI schema generation."""

from __future__ import annotations

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TMDBMovieData(BaseModel):
    """TMDB Movie data subset for API responses."""

    media_type: str = Field(default="movie", description="Media type identifier")
    id: int = Field(description="TMDB movie ID")
    title: str = Field(description="Movie title")
    overview: Optional[str] = Field(None, description="Movie overview/description")
    poster_path: Optional[str] = Field(None, description="Poster image path")
    backdrop_path: Optional[str] = Field(None, description="Backdrop image path")
    release_date: Optional[str] = Field(None, description="Release date (YYYY-MM-DD)")
    vote_average: Optional[float] = Field(None, description="Average vote score")
    vote_count: Optional[int] = Field(None, description="Number of votes")
    popularity: Optional[float] = Field(None, description="Popularity score")
    runtime: Optional[int] = Field(None, description="Runtime in minutes")
    genres: Optional[List[Dict[str, Union[int, str]]]] = Field(
        None, description="List of genres with id and name"
    )
    production_companies: Optional[List[Dict[str, Union[int, str]]]] = Field(
        None, description="Production companies"
    )
    original_language: Optional[str] = Field(None, description="Original language code")
    budget: Optional[int] = Field(None, description="Movie budget")
    revenue: Optional[int] = Field(None, description="Movie revenue")

    # Additional metadata that might be included
    videos: Optional[Dict[str, List[Dict[str, Union[str, int, bool]]]]] = Field(
        None, description="Associated videos (trailers, etc.)"
    )
    images: Optional[Dict[str, List[Dict[str, Union[str, int, float]]]]] = Field(
        None, description="Associated images"
    )
    external_ids: Optional[Dict[str, Optional[Union[str, int]]]] = Field(
        None, description="External service IDs (IMDb, etc.)"
    )


class TMDBTVData(BaseModel):
    """TMDB TV Show data subset for API responses."""

    media_type: str = Field(default="tv", description="Media type identifier")
    id: int = Field(description="TMDB TV show ID")
    name: str = Field(description="TV show name")
    overview: Optional[str] = Field(None, description="TV show overview/description")
    poster_path: Optional[str] = Field(None, description="Poster image path")
    backdrop_path: Optional[str] = Field(None, description="Backdrop image path")
    first_air_date: Optional[str] = Field(
        None, description="First air date (YYYY-MM-DD)"
    )
    last_air_date: Optional[str] = Field(None, description="Last air date (YYYY-MM-DD)")
    vote_average: Optional[float] = Field(None, description="Average vote score")
    vote_count: Optional[int] = Field(None, description="Number of votes")
    popularity: Optional[float] = Field(None, description="Popularity score")
    number_of_episodes: Optional[int] = Field(
        None, description="Total number of episodes"
    )
    number_of_seasons: Optional[int] = Field(
        None, description="Total number of seasons"
    )
    genres: Optional[List[Dict[str, Union[int, str]]]] = Field(
        None, description="List of genres with id and name"
    )
    networks: Optional[List[Dict[str, Union[int, str]]]] = Field(
        None, description="Broadcasting networks"
    )
    production_companies: Optional[List[Dict[str, Union[int, str]]]] = Field(
        None, description="Production companies"
    )
    original_language: Optional[str] = Field(None, description="Original language code")
    origin_country: Optional[List[str]] = Field(None, description="Countries of origin")
    status: Optional[str] = Field(
        None, description="Show status (Ended, Returning, etc.)"
    )
    type: Optional[str] = Field(None, description="Show type (Scripted, Reality, etc.)")

    # Additional metadata that might be included
    videos: Optional[Dict[str, List[Dict[str, Union[str, int, bool]]]]] = Field(
        None, description="Associated videos (trailers, etc.)"
    )
    images: Optional[Dict[str, List[Dict[str, Union[str, int, float]]]]] = Field(
        None, description="Associated images"
    )
    external_ids: Optional[Dict[str, Optional[Union[str, int]]]] = Field(
        None, description="External service IDs (IMDb, TVDB, etc.)"
    )


class AniListMediaData(BaseModel):
    """AniList media data subset for API responses."""

    id: int = Field(description="AniList media ID")
    title: Optional[Dict[str, Optional[str]]] = Field(
        None,
        description="Title in different languages",
        example={
            "userPreferred": "Attack on Titan",
            "romaji": "Shingeki no Kyojin",
            "english": "Attack on Titan",
            "native": "進撃の巨人",
        },
    )
    description: Optional[str] = Field(None, description="Media description")
    coverImage: Optional[Dict[str, Optional[str]]] = Field(
        None,
        description="Cover image URLs",
        example={
            "extraLarge": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx16498-C6FPmWm59CyP.jpg",
            "large": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx16498-C6FPmWm59CyP.jpg",
            "medium": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/small/bx16498-C6FPmWm59CyP.jpg",
            "color": "#e4a15d",
        },
    )
    bannerImage: Optional[str] = Field(None, description="Banner image URL")
    startDate: Optional[Dict[str, Optional[int]]] = Field(
        None, description="Start date", example={"year": 2013, "month": 4, "day": 7}
    )
    endDate: Optional[Dict[str, Optional[int]]] = Field(
        None, description="End date", example={"year": 2013, "month": 9, "day": 29}
    )
    season: Optional[str] = Field(
        None, description="Anime season (WINTER, SPRING, SUMMER, FALL)"
    )
    seasonYear: Optional[int] = Field(None, description="Year of the season")
    episodes: Optional[int] = Field(None, description="Number of episodes")
    duration: Optional[int] = Field(None, description="Episode duration in minutes")
    chapters: Optional[int] = Field(None, description="Number of chapters (manga)")
    volumes: Optional[int] = Field(None, description="Number of volumes (manga)")
    genres: Optional[List[str]] = Field(None, description="List of genres")
    synonyms: Optional[List[str]] = Field(None, description="Alternative titles")
    averageScore: Optional[int] = Field(None, description="Average score (0-100)")
    meanScore: Optional[int] = Field(None, description="Mean score (0-100)")
    popularity: Optional[int] = Field(None, description="Popularity ranking")
    favourites: Optional[int] = Field(None, description="Number of users who favorited")
    source: Optional[str] = Field(
        None, description="Source material (ORIGINAL, MANGA, etc.)"
    )
    status: Optional[str] = Field(
        None, description="Release status (FINISHED, RELEASING, etc.)"
    )
    format: Optional[str] = Field(
        None, description="Media format (TV, MOVIE, OVA, etc.)"
    )
    type: Optional[str] = Field(None, description="Media type (ANIME, MANGA)")
    countryOfOrigin: Optional[str] = Field(None, description="Country of origin")
    isAdult: Optional[bool] = Field(None, description="Whether content is adult-rated")

    # Nested objects (simplified)
    trailer: Optional[Dict[str, Optional[str]]] = Field(
        None,
        description="Trailer information",
        example={"id": "PfuNSVDqPiks", "site": "youtube"},
    )
    nextAiringEpisode: Optional[Dict[str, Optional[Union[int, str]]]] = Field(
        None, description="Next airing episode info"
    )
    studios: Optional[Dict[str, List[Dict[str, Union[int, str, bool]]]]] = Field(
        None, description="Animation studios"
    )
    tags: Optional[List[Dict[str, Union[int, str, bool]]]] = Field(
        None, description="Content tags"
    )


# Union type for TMDB data (discriminated by media_type)
TMDBData = Union[TMDBMovieData, TMDBTVData]

# Type aliases for better readability
AniListData = AniListMediaData
