"""Anime sources API router with comprehensive OpenAPI documentation."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from fastapi.responses import JSONResponse

from lib.models.responses import (
    DetailResponse,
    EpisodeResponse,
    LatestResponse,
    MovieResponse,
    MoviesResponse,
    PopularResponse,
    SearchResponse,
    SeasonResponse,
    SeasonsResponse,
    SeriesDetailResponse,
    VideoListResponse,
)
from lib.services.anime_service import AnimeService

from ..dependencies import get_anime_service

router = APIRouter(
    prefix="/sources",
    tags=["anime-sources"],
    responses={
        404: {"description": "Source not found"},
        500: {"description": "Internal server error"},
    },
)


@router.get(
    "/",
    summary="Get Available Anime Sources",
    description="Retrieve a list of all available anime streaming sources.",
    response_description="List of available anime sources",
    responses={
        200: {
            "description": "Successfully retrieved sources",
            "content": {
                "application/json": {
                    "example": {"sources": ["aniworld", "serienstream"]}
                }
            },
        }
    },
)
async def get_sources(anime_service: AnimeService = Depends(get_anime_service)):
    """
    Get all available anime sources.

    Returns a list of source identifiers that can be used with other endpoints
    to access anime content from different streaming platforms.
    """
    return {"sources": anime_service.get_available_sources()}


@router.get(
    "/{source}/preferences",
    summary="Get Source Preferences",
    description="Retrieve configuration preferences for a specific anime source.",
    response_description="Source preferences configuration",
    responses={
        200: {
            "description": "Successfully retrieved preferences",
            "content": {
                "application/json": {
                    "example": {
                        "preferences": [
                            {
                                "key": "lang",
                                "list_preference": {
                                    "title": "Bevorzugte Sprache",
                                    "entries": ["Deutsch", "Englisch"],
                                    "entryValues": ["Deutscher", "Englischer"],
                                },
                            }
                        ]
                    }
                }
            },
        }
    },
)
async def get_source_preferences(
    source: str = Path(
        ..., description="Source identifier (e.g., 'aniworld', 'serienstream')"
    ),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get configuration preferences for a specific anime source.

    Preferences control playback settings like language, quality, and host preferences.
    """
    try:
        preferences = anime_service.get_source_preferences(source)
        return {"preferences": preferences}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{source}/popular",
    response_model=PopularResponse,
    summary="Get Popular Anime",
    description="Retrieve a list of popular anime from the specified source.",
    response_description="List of popular anime with pagination info",
    responses={
        200: {
            "description": "Successfully retrieved popular anime",
            "content": {
                "application/json": {
                    "example": {
                        "list": [
                            {
                                "name": "Attack on Titan",
                                "image_url": "https://example.com/image.jpg",
                                "link": "/anime/stream/attack-on-titan",
                            }
                        ],
                        "has_next_page": False,
                    }
                }
            },
        }
    },
)
async def get_popular(
    source: str = Path(..., description="Source identifier"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get popular anime from the specified source.

    Returns a paginated list of anime sorted by popularity on the source platform.
    """
    try:
        return await anime_service.get_popular(source, page)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/latest",
    response_model=LatestResponse,
    summary="Get Latest Updates",
    description="Retrieve the latest anime updates from the specified source.",
    response_description="List of recently updated anime",
)
async def get_latest_updates(
    source: str = Path(..., description="Source identifier"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get latest anime updates from the specified source.

    Returns recently updated anime with new episodes or content.
    """
    try:
        return await anime_service.get_latest_updates(source, page)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/search",
    response_model=SearchResponse,
    summary="Search Anime",
    description="Search for anime by title in the specified source.",
    response_description="List of anime matching the search query",
)
async def search_anime(
    source: str = Path(..., description="Source identifier"),
    q: str = Query(..., description="Search query (anime title)", min_length=1),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    lang: str = Query(None, description="Language filter (de, en, sub, all)"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Search for anime by title in the specified source.

    Performs a text search across anime titles and returns matching results.
    """
    try:
        return await anime_service.search(source, q, page, lang)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/detail",
    response_model=DetailResponse,
    summary="Get Anime Details (Legacy)",
    description="Get detailed information about a specific anime including flat episodes list.",
    response_description="Detailed anime information with flat episodes structure",
    responses={
        200: {
            "description": "Successfully retrieved anime details",
            "content": {
                "application/json": {
                    "example": {
                        "anime": {
                            "name": "Attack on Titan",
                            "image_url": "https://example.com/image.jpg",
                            "description": "Anime description...",
                            "author": "Hajime Isayama",
                            "status": 5,
                            "genre": ["Action", "Drama"],
                            "episodes": [
                                {
                                    "name": "Staffel 4 Folge 30 : The Final Chapter Part 2",
                                    "url": "/anime/stream/attack-on-titan/staffel-4/episode-30",
                                    "date_upload": None,
                                }
                            ],
                        }
                    }
                }
            },
        }
    },
    deprecated=True,
)
async def get_anime_detail(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    flat: bool = Query(False, description="Return flat episodes (legacy format)"),
    response: Response = None,
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get detailed information about a specific anime (Legacy Endpoint).

    **⚠️ DEPRECATED:** This endpoint returns episodes in a flat structure.
    Use `/sources/{source}/series` for the new hierarchical structure with seasons and movies.

    Returns comprehensive anime information including metadata and a flat list of all episodes.
    """
    try:
        if flat:
            # Add deprecation warning for flat format
            response.headers["Deprecation"] = "true"
            response.headers["Link"] = (
                f'</sources/{source}/series>; rel="successor-version"'
            )
            return await anime_service.get_detail(source, url)
        else:
            return await anime_service.get_detail(source, url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/videos",
    response_model=VideoListResponse,
    summary="Get Video Sources",
    description="Get available video streams for a specific episode with optional language preference.",
    response_description="List of video sources with different hosts and qualities",
)
async def get_video_sources(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Episode URL path"),
    lang: str = Query(
        None, description="Preferred language (e.g., 'Deutscher', 'Englischer')"
    ),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get video sources for a specific episode with optional language preference.

    Returns available video streams from different hosting providers with various
    quality options and language/subtitle configurations. If a preferred language
    is specified and no videos are found in that language, the system will fallback
    to the first available language.
    """
    try:
        return await anime_service.get_video_list(source, url, lang)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== NEW HIERARCHICAL API ENDPOINTS ==========


@router.get(
    "/{source}/series",
    response_model=SeriesDetailResponse,
    summary="Get Series Detail (Hierarchical)",
    description="Get anime series with episodes organized by seasons and movies/OVAs separately.",
    response_description="Hierarchical series structure with seasons and movies",
    responses={
        200: {
            "description": "Successfully retrieved hierarchical series detail",
            "content": {
                "application/json": {
                    "example": {
                        "series": {
                            "slug": "attack-on-titan",
                            "seasons": [
                                {
                                    "season": 4,
                                    "title": "Staffel 4",
                                    "episodes": [
                                        {
                                            "season": 4,
                                            "episode": 30,
                                            "title": "The Final Chapter Part 2",
                                            "url": "/anime/stream/attack-on-titan/staffel-4/episode-30",
                                            "date_upload": None,
                                            "tags": ["Series Final Episode"],
                                        }
                                    ],
                                }
                            ],
                            "movies": [
                                {
                                    "number": 12,
                                    "title": "The Last Attack",
                                    "kind": "movie",
                                    "url": "/anime/stream/attack-on-titan/filme/film-12",
                                    "date_upload": None,
                                    "tags": [],
                                }
                            ],
                        }
                    }
                }
            },
        }
    },
    tags=["hierarchical-api"],
)
async def get_series_detail(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get anime series with hierarchical episode organization.

    **🆕 NEW ENDPOINT:** Returns episodes organized by seasons and movies/OVAs/specials
    separately, providing a better structure for frontend applications.

    **Features:**
    - Episodes grouped by season number
    - Movies/OVAs/specials in separate collection
    - Extracted tags from episode names
    - Automatic sorting by season/episode numbers
    - Clean title extraction without German prefixes
    """
    try:
        return await anime_service.get_series_detail(source, url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/series/seasons",
    response_model=SeasonsResponse,
    summary="Get All Seasons",
    description="Get list of all seasons for a series.",
    response_description="List of all seasons with their episodes",
    tags=["hierarchical-api"],
)
async def get_series_seasons(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get all seasons for a series.

    Returns a complete list of all seasons with their episodes, sorted by season number.
    """
    try:
        series_detail = await anime_service.get_series_detail(source, url)
        return SeasonsResponse(seasons=series_detail.series.seasons)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/series/seasons/{season_num}",
    response_model=SeasonResponse,
    summary="Get Specific Season",
    description="Get details for a specific season including all its episodes.",
    response_description="Season details with all episodes",
    responses={404: {"description": "Season not found"}},
    tags=["hierarchical-api"],
)
async def get_series_season(
    source: str = Path(..., description="Source identifier"),
    season_num: int = Path(..., description="Season number", ge=1),
    url: str = Query(..., description="Anime URL path"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get details for a specific season.

    Returns all episodes for the specified season number, sorted by episode number.
    """
    try:
        series_detail = await anime_service.get_series_detail(source, url)
        for season in series_detail.series.seasons:
            if season.season == season_num:
                return SeasonResponse(season=season)
        raise HTTPException(status_code=404, detail=f"Season {season_num} not found")
    except HTTPException:
        # Re-raise HTTPExceptions (like our 404) without wrapping them
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/series/seasons/{season_num}/episodes/{episode_num}",
    response_model=EpisodeResponse,
    summary="Get Specific Episode",
    description="Get details for a specific episode within a season.",
    response_description="Episode details",
    responses={404: {"description": "Season or episode not found"}},
    tags=["hierarchical-api"],
)
async def get_series_episode(
    source: str = Path(..., description="Source identifier"),
    season_num: int = Path(..., description="Season number", ge=1),
    episode_num: int = Path(..., description="Episode number", ge=1),
    url: str = Query(..., description="Anime URL path"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get details for a specific episode.

    Returns detailed information for a specific episode within a season,
    including title, URL, tags, and metadata.
    """
    try:
        series_detail = await anime_service.get_series_detail(source, url)
        for season in series_detail.series.seasons:
            if season.season == season_num:
                for episode in season.episodes:
                    if episode.episode == episode_num:
                        return EpisodeResponse(episode=episode)
                raise HTTPException(
                    status_code=404,
                    detail=f"Episode {episode_num} not found in season {season_num}",
                )
        raise HTTPException(status_code=404, detail=f"Season {season_num} not found")
    except HTTPException:
        # Re-raise HTTPExceptions (like our 404) without wrapping them
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/series/movies",
    response_model=MoviesResponse,
    summary="Get All Movies/OVAs",
    description="Get list of all movies, OVAs, and specials for a series.",
    response_description="List of movies, OVAs, and specials",
    responses={
        200: {
            "description": "Successfully retrieved movies",
            "content": {
                "application/json": {
                    "example": {
                        "movies": [
                            {
                                "number": 12,
                                "title": "The Last Attack",
                                "kind": "movie",
                                "url": "/anime/stream/attack-on-titan/filme/film-12",
                                "date_upload": None,
                                "tags": [],
                            },
                            {
                                "number": 11,
                                "title": "Great need",
                                "kind": "ova",
                                "url": "/anime/stream/attack-on-titan/filme/film-11",
                                "date_upload": None,
                                "tags": [],
                            },
                        ]
                    }
                }
            },
        }
    },
    tags=["hierarchical-api"],
)
async def get_series_movies(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get all movies, OVAs, and specials for a series.

    Returns a complete list of all non-episodic content including movies,
    OVAs (Original Video Animations), and special episodes, sorted by number.
    """
    try:
        series_detail = await anime_service.get_series_detail(source, url)
        return MoviesResponse(movies=series_detail.series.movies)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{source}/series/movies/{movie_num}",
    response_model=MovieResponse,
    summary="Get Specific Movie/OVA",
    description="Get details for a specific movie, OVA, or special by number.",
    response_description="Movie/OVA/special details",
    responses={404: {"description": "Movie not found"}},
    tags=["hierarchical-api"],
)
async def get_series_movie(
    source: str = Path(..., description="Source identifier"),
    movie_num: int = Path(..., description="Movie/OVA number", ge=1),
    url: str = Query(..., description="Anime URL path"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get details for a specific movie, OVA, or special.

    Returns detailed information for a specific movie/OVA/special by its number,
    including title, kind (movie/ova/special), URL, and tags.
    """
    try:
        series_detail = await anime_service.get_series_detail(source, url)
        for movie in series_detail.series.movies:
            if movie.number == movie_num:
                return MovieResponse(movie=movie)
        raise HTTPException(status_code=404, detail=f"Movie {movie_num} not found")
    except HTTPException:
        # Re-raise HTTPExceptions (like our 404) without wrapping them
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ========== BACKWARD COMPATIBILITY ENDPOINTS ==========


@router.get(
    "/{source}/episodes",
    response_model=DetailResponse,
    summary="Get Episodes (Flat) - DEPRECATED",
    description="⚠️ DEPRECATED: Get episodes in flat format for backward compatibility.",
    response_description="Anime details with flat episodes list",
    deprecated=True,
    responses={
        200: {
            "description": "Successfully retrieved episodes (flat format)",
            "headers": {
                "Deprecation": {
                    "description": "Indicates this endpoint is deprecated",
                    "schema": {"type": "string"},
                },
                "Link": {
                    "description": "Link to successor version",
                    "schema": {"type": "string"},
                },
                "Warning": {
                    "description": "Deprecation warning message",
                    "schema": {"type": "string"},
                },
            },
        }
    },
    tags=["legacy-endpoints"],
)
async def get_episodes_flat(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    response: Response = None,
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get episodes in flat format (DEPRECATED).

    **⚠️ DEPRECATED:** This endpoint is maintained for backward compatibility only.

    **Migration Guide:**
    - Use `GET /sources/{source}/series` for hierarchical structure
    - Episodes will be organized by seasons with movies/OVAs separate
    - Better performance and structure for modern applications

    **Deprecation Timeline:**
    - Will be removed in v2.0.0
    - Please migrate to the new hierarchical endpoints
    """
    # Add deprecation warning headers
    if response:
        response.headers["Deprecation"] = "true"
        response.headers["Link"] = (
            f'</sources/{source}/series>; rel="successor-version"'
        )
        response.headers["Warning"] = (
            '299 - "This endpoint is deprecated. Use /series for hierarchical structure."'
        )

    try:
        return await anime_service.get_detail(source, url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
