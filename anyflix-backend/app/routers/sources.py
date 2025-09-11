"""Anime sources API router with comprehensive OpenAPI documentation."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from fastapi.responses import JSONResponse

from lib.models.responses import (
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
    tags=["media-api"],
    responses={
        404: {"description": "Source not found"},
        500: {"description": "Internal server error"},
    },
)


@router.get(
    "/",
    summary="📋 List Available Sources",
    description="**Source Management**: Retrieve a list of all available streaming sources for media content.",
    response_description="List of available streaming sources",
    operation_id="list_sources",
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
    summary="📋 Get Source Configuration",
    description="**Source Management**: Retrieve configuration preferences for a specific streaming source including language, quality, and host settings.",
    response_description="Source preferences configuration",
    operation_id="get_source_preferences",
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
    summary="🔍 Get Popular Content",
    description="**Content Discovery**: Retrieve a list of popular media content from the specified source, sorted by popularity rankings.",
    response_description="List of popular content with pagination info",
    operation_id="get_popular_content",
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
    summary="🔍 Get Latest Updates",
    description="**Content Discovery**: Retrieve the latest media updates from the specified source with new episodes or content.",
    response_description="List of recently updated content",
    operation_id="get_latest_updates",
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
    summary="🔍 Search Content",
    description="**Content Discovery**: Search for media content by title in the specified source with optional language filtering.",
    response_description="List of content matching the search query",
    operation_id="search_content",
)
async def search_content(
    source: str = Path(..., description="Source identifier"),
    q: str = Query(..., description="Search query (content title)", min_length=1),
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
    "/{source}/videos",
    response_model=VideoListResponse,
    summary="🎬 Get Video Streaming Links",
    description="**Video Sources**: Get available video streams for a specific episode with optional language preference and multiple hosting providers.",
    response_description="List of video sources with different hosts and qualities",
    operation_id="get_video_sources",
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


# ========== SERIES STRUCTURE ENDPOINTS ==========


@router.get(
    "/{source}/series",
    response_model=SeriesDetailResponse,
    summary="📺 Get Full Series Data",
    description="**Series Structure**: Get complete media series with episodes organized by seasons and movies/specials separately.",
    response_description="Hierarchical series structure with seasons and movies",
    operation_id="get_series_detail",
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
    tags=["media-api"],
)
async def get_series_detail(
    source: str = Path(..., description="Source identifier"),
    url: str = Query(..., description="Anime URL path"),
    anime_service: AnimeService = Depends(get_anime_service),
):
    """
    Get anime series with hierarchical episode organization.

    **🆕 NEW ENDPOINT:** Returns episodes organized by seasons and movies/specials
    separately, providing a better structure for frontend applications.

    **Features:**
    - Episodes grouped by season number
    - Movies/specials in separate collection
    - Extracted tags from episode names
    - Automatic sorting by season/episode numbers
    - Clean title extraction
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
    summary="📺 Get All Seasons",
    description="**Series Structure**: Get list of all seasons for a series with their episodes, sorted by season number.",
    response_description="List of all seasons with their episodes",
    operation_id="get_all_seasons",
    tags=["media-api"],
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
    summary="📺 Get Specific Season",
    description="**Series Structure**: Get details for a specific season including all its episodes, sorted by episode number.",
    response_description="Season details with all episodes",
    operation_id="get_season_detail",
    responses={404: {"description": "Season not found"}},
    tags=["media-api"],
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
    summary="📺 Get Specific Episode",
    description="**Series Structure**: Get details for a specific episode within a season, including title, URL, tags, and metadata.",
    response_description="Episode details",
    operation_id="get_episode_detail",
    responses={404: {"description": "Season or episode not found"}},
    tags=["media-api"],
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
    summary="📺 Get All Movies/OVAs",
    description="**Series Structure**: Get list of all movies, OVAs, and specials for a series, sorted by number.",
    response_description="List of movies, OVAs, and specials",
    operation_id="get_all_movies",
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
    tags=["media-api"],
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
    summary="📺 Get Specific Movie/OVA",
    description="**Series Structure**: Get details for a specific movie, OVA, or special by number, including title, kind, URL, and tags.",
    response_description="Movie/OVA/special details",
    operation_id="get_movie_detail",
    responses={404: {"description": "Movie not found"}},
    tags=["media-api"],
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
