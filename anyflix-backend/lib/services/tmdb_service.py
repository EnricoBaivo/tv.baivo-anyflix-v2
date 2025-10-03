"""TMDB (The Movie Database) service."""

import json
import logging
import os

import httpx

from lib.models.tmdb import (
    TMDBConfiguration,
    TMDBMovieDetail,
    TMDBSearchResponse,
    TMDBTVDetail,
)
from lib.utils.caching import ServiceCacheConfig, cached
from lib.utils.client import HTTPClient

logger = logging.getLogger(__name__)


class TMDBService:
    """Service for interacting with The Movie Database API."""

    def __init__(
        self, api_key: str | None = None, base_url: str = "https://api.themoviedb.org/3"
    ) -> None:
        """Initialize TMDB service.

        Args:
            api_key: TMDB API key
            base_url: TMDB API base URL
        """
        self.api_key = os.getenv("TMDB_API_KEY") if api_key is None else api_key.strip()
        self.base_url = base_url
        self.client = HTTPClient()
        self._configuration: TMDBConfiguration | None = None
        self._api_available = bool(api_key)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    def _get_headers(self) -> dict[str, str]:
        """Get headers for TMDB API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @cached(ttl=ServiceCacheConfig.TMDB_CONFIG_TTL, key_prefix="tmdb_configuration")
    async def get_configuration(self) -> TMDBConfiguration:
        """Get TMDB API configuration."""
        if self._configuration:
            return self._configuration

        url = f"{self.base_url}/configuration"
        params = {"api_key": self.api_key}
        params["language"] = "de-DE"

        response = await self.client.get(
            url, params=params, headers=self._get_headers()
        )
        response_data = json.loads(response.body)
        self._configuration = TMDBConfiguration(**response_data)
        return self._configuration

    @cached(ttl=ServiceCacheConfig.TMDB_SEARCH_TTL, key_prefix="tmdb_search_multi")
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
                "include_adult": "true",
                "language": "de-DE",
            }

            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response_data = json.loads(response.body)

            # Check if TMDB returned an error response
            if "success" in response_data and not response_data["success"]:
                logger.warning(
                    "TMDB API error: %s (status_code: %s)",
                    response_data.get("status_message", "Unknown error"),
                    response_data.get("status_code", "Unknown"),
                )
                return TMDBSearchResponse(
                    page=page, results=[], total_pages=0, total_results=0
                )

            try:
                return TMDBSearchResponse(**response_data)
            except (ValueError, TypeError, KeyError) as e:
                logger.exception(
                    "Pydantic validation error in search_multi for query '%s'", query
                )
                logger.debug(
                    "Response data that caused validation error: %s", response_data
                )
                # Return empty response instead of crashing
                return TMDBSearchResponse(
                    page=page, results=[], total_pages=0, total_results=0
                )

        except (httpx.HTTPError, ValueError, KeyError):
            logger.exception("Failed to search TMDB")
            return TMDBSearchResponse(
                page=page, results=[], total_pages=0, total_results=0
            )

    @cached(ttl=ServiceCacheConfig.TMDB_DETAILS_TTL, key_prefix="tmdb_movie_details")
    async def get_movie_details(
        self, movie_id: int, append_to_response: str | None = None
    ) -> TMDBMovieDetail | None:
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
                params["include_adult"] = "true"
                params["language"] = "de-DE"

            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response_data = json.loads(response.body)
            return TMDBMovieDetail(**response_data)

        except (httpx.HTTPError, ValueError, KeyError):
            logger.exception("Failed to get movie details for ID %s", movie_id)
            return None

    @cached(ttl=ServiceCacheConfig.TMDB_DETAILS_TTL, key_prefix="tmdb_tv_details")
    async def get_tv_details(
        self, tv_id: int, append_to_response: str | None = None
    ) -> TMDBTVDetail | None:
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
                params["include_adult"] = "true"
                params["language"] = "de-DE"

            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response_data = json.loads(response.body)
            return TMDBTVDetail(**response_data)

        except (httpx.HTTPError, ValueError, KeyError):
            logger.exception("Failed to get TV details for ID %s", tv_id)
            return None

    @cached(ttl=ServiceCacheConfig.TMDB_SEARCH_TTL, key_prefix="tmdb_find_external")
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
            params["include_adult"] = "true"
            params["language"] = "de-DE"
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

        except (httpx.HTTPError, ValueError, KeyError):
            logger.exception("Failed to find by external ID %s", external_id)
            return TMDBSearchResponse(
                page=1, results=[], total_pages=0, total_results=0
            )

    @cached(ttl=ServiceCacheConfig.TMDB_CONFIG_TTL, key_prefix="tmdb_image_url")
    async def get_image_url(self, path: str | None, size: str = "w500") -> str | None:
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
