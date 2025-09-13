"""TMDB (The Movie Database) service."""

import asyncio
import json
import logging
from typing import Dict, List, Optional

import aiohttp

from lib.models.tmdb import (
    TMDBConfiguration,
    TMDBMovieDetail,
    TMDBSearchResponse,
    TMDBTVDetail,
)
from lib.utils.client import HTTPClient

logger = logging.getLogger(__name__)


class TMDBService:
    """Service for interacting with The Movie Database API."""

    def __init__(self, api_key: str, base_url: str = "https://api.themoviedb.org/3"):
        """Initialize TMDB service.

        Args:
            api_key: TMDB API key
            base_url: TMDB API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = HTTPClient()
        self._configuration: Optional[TMDBConfiguration] = None
        self._api_available = bool(api_key.strip())

    async def __aenter__(self):
        """Async context manager entry."""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for TMDB API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def get_configuration(self) -> TMDBConfiguration:
        """Get TMDB API configuration."""
        if self._configuration:
            return self._configuration

        try:
            url = f"{self.base_url}/configuration"
            params = {"api_key": self.api_key}

            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response_data = json.loads(response.body)
            self._configuration = TMDBConfiguration(**response_data)
            return self._configuration

        except Exception as e:
            logger.error(f"Failed to get TMDB configuration: {e}")
            # Return default configuration
            return TMDBConfiguration(
                images={
                    "base_url": "https://image.tmdb.org/t/p/",
                    "secure_base_url": "https://image.tmdb.org/t/p/",
                    "backdrop_sizes": ["w300", "w780", "w1280", "original"],
                    "logo_sizes": [
                        "w45",
                        "w92",
                        "w154",
                        "w185",
                        "w300",
                        "w500",
                        "original",
                    ],
                    "poster_sizes": [
                        "w92",
                        "w154",
                        "w185",
                        "w342",
                        "w500",
                        "w780",
                        "original",
                    ],
                    "profile_sizes": ["w45", "w185", "h632", "original"],
                    "still_sizes": ["w92", "w185", "w300", "original"],
                },
                change_keys=[],
            )

    async def search_multi(self, query: str, page: int = 1) -> TMDBSearchResponse:
        """Search for movies and TV shows.

        Args:
            query: Search query
            page: Page number

        Returns:
            Search response with results
        """
        try:
            url = f"{self.base_url}/search/multi"
            params = {
                "api_key": self.api_key,
                "query": query,
                "page": page,
                "include_adult": "false",
            }

            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response_data = json.loads(response.body)
            return TMDBSearchResponse(**response_data)

        except Exception as e:
            logger.error(f"Failed to search TMDB: {e}")
            return TMDBSearchResponse(
                page=page, results=[], total_pages=0, total_results=0
            )

    async def get_movie_details(
        self, movie_id: int, append_to_response: Optional[str] = None
    ) -> Optional[TMDBMovieDetail]:
        """Get movie details by ID.

        Args:
            movie_id: TMDB movie ID
            append_to_response: Additional data to append (e.g., "videos,images,external_ids")

        Returns:
            Movie details or None if not found
        """
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {"api_key": self.api_key}

            if append_to_response:
                params["append_to_response"] = append_to_response

            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response_data = json.loads(response.body)
            return TMDBMovieDetail(**response_data)

        except Exception as e:
            logger.error(f"Failed to get movie details for ID {movie_id}: {e}")
            return None

    async def get_tv_details(
        self, tv_id: int, append_to_response: Optional[str] = None
    ) -> Optional[TMDBTVDetail]:
        """Get TV show details by ID.

        Args:
            tv_id: TMDB TV show ID
            append_to_response: Additional data to append (e.g., "videos,images,external_ids")

        Returns:
            TV show details or None if not found
        """
        try:
            url = f"{self.base_url}/tv/{tv_id}"
            params = {"api_key": self.api_key}

            if append_to_response:
                params["append_to_response"] = append_to_response

            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response_data = json.loads(response.body)
            return TMDBTVDetail(**response_data)

        except Exception as e:
            logger.error(f"Failed to get TV details for ID {tv_id}: {e}")
            return None

    async def find_by_external_id(
        self, external_id: str, external_source: str
    ) -> TMDBSearchResponse:
        """Find media by external ID.

        Args:
            external_id: External ID (e.g., IMDb ID)
            external_source: External source (e.g., "imdb_id", "tvdb_id")

        Returns:
            Search response with results
        """
        try:
            url = f"{self.base_url}/find/{external_id}"
            params = {"api_key": self.api_key, "external_source": external_source}

            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response_data = json.loads(response.body)

            # Convert find response to search response format
            results = []
            for media_type in ["movie_results", "tv_results"]:
                if media_type in response_data:
                    for item in response_data[media_type]:
                        item["media_type"] = (
                            "movie" if media_type == "movie_results" else "tv"
                        )
                        results.append(item)

            return TMDBSearchResponse(
                page=1, results=results, total_pages=1, total_results=len(results)
            )

        except Exception as e:
            logger.error(f"Failed to find by external ID {external_id}: {e}")
            return TMDBSearchResponse(
                page=1, results=[], total_pages=0, total_results=0
            )

    async def get_image_url(
        self, path: Optional[str], size: str = "w500"
    ) -> Optional[str]:
        """Get full image URL from TMDB path.

        Args:
            path: TMDB image path
            size: Image size

        Returns:
            Full image URL or None
        """
        if not path:
            return None

        config = await self.get_configuration()
        base_url = config.images.get("secure_base_url", "https://image.tmdb.org/t/p/")
        return f"{base_url}{size}{path}"

    async def search_and_match(
        self, title: str, year: Optional[int] = None, media_type: Optional[str] = None
    ) -> Optional[Dict]:
        """Search and find the best match for a title.

        Args:
            title: Title to search for
            year: Release year for better matching
            media_type: Preferred media type ("movie" or "tv")

        Returns:
            Best match details or None
        """
        if not self._api_available:
            logger.warning("TMDB API key not available, skipping search")
            return None

        try:
            # Search for the title
            search_results = await self.search_multi(title)

            if not search_results.results:
                return None

            # Find best match
            best_match = None
            best_score = 0

            for result in search_results.results:
                # Skip person results - we only want movies and TV shows
                if result.media_type == "person":
                    continue
                    
                score = 0

                # Title similarity (basic check)
                result_title = result.title or result.name or ""
                if (
                    title.lower() in result_title.lower()
                    or result_title.lower() in title.lower()
                ):
                    score += 50

                # Year matching
                if year:
                    result_year = None
                    if result.release_date:
                        result_year = int(result.release_date[:4])
                    elif result.first_air_date:
                        result_year = int(result.first_air_date[:4])

                    if result_year and abs(result_year - year) <= 1:
                        score += 30

                # Media type preference
                if media_type and result.media_type == media_type:
                    score += 20

                # Popularity bonus
                score += min((result.popularity or 0) / 100, 10)

                if score > best_score:
                    best_score = score
                    best_match = result

            if not best_match:
                return None

            # Get detailed information
            if best_match.media_type == "movie":
                details = await self.get_movie_details(
                    best_match.id, append_to_response="videos,images,external_ids"
                )
            else:
                details = await self.get_tv_details(
                    best_match.id, append_to_response="videos,images,external_ids"
                )

            return details.dict() if details else None

        except Exception as e:
            logger.error(f"Failed to search and match title '{title}': {e}")
            return None
