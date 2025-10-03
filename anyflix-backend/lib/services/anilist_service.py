"""AniList API service for GraphQL queries."""

import asyncio
import time
from typing import Any

import aiohttp
from pydantic import ValidationError

from lib.models.anilist import (
    Media,
    MediaByIdVariables,
    MediaPageResponse,
    MediaResponse,
    MediaSearchVariables,
    MediaType,
    PageResponse,
)
from lib.utils.caching import ServiceCacheConfig, cached
from lib.utils.logging_config import get_logger, timed_operation


class AniListService:
    """Service for interacting with AniList GraphQL API."""

    BASE_URL = "https://graphql.anilist.co"

    # GraphQL query for detailed media information
    MEDIA_QUERY = """
    query media($id: Int, $search: String, $type: MediaType) {
      Media(id: $id, search: $search, type: $type) {
        id
        trailer {
          id
          site
        }
        title {
          userPreferred
          romaji
          english
          native
        }
        coverImage {
          extraLarge
          large
        }
        bannerImage
        startDate {
          year
          month
          day
        }
        endDate {
          year
          month
          day
        }
        description
        season
        seasonYear
        type
        format
        status(version: 2)
        episodes
        duration
        chapters
        volumes
        genres
        synonyms
        source(version: 3)
        isAdult
        isLocked
        meanScore
        averageScore
        popularity
        favourites
        isFavouriteBlocked
        hashtag
        countryOfOrigin
        isLicensed
        isFavourite
        isRecommendationBlocked
        isFavouriteBlocked
        isReviewBlocked
        nextAiringEpisode {
          airingAt
          timeUntilAiring
          episode
        }
        relations {
          edges {
            id
            relationType(version: 2)
            node {
              id
              title {
                userPreferred
              }
              format
              type
              status(version: 2)
              bannerImage
              coverImage {
                large
              }
            }
          }
        }
        characterPreview: characters(perPage: 6, sort: [ROLE, RELEVANCE, ID]) {
          edges {
            id
            role
            name
            voiceActors(language: JAPANESE, sort: [RELEVANCE, ID]) {
              id
              name {
                userPreferred
              }
              language: languageV2
              image {
                large
              }
            }
            node {
              id
              name {
                userPreferred
              }
              image {
                large
              }
            }
          }
        }
        staffPreview: staff(perPage: 8, sort: [RELEVANCE, ID]) {
          edges {
            id
            role
            node {
              id
              name {
                userPreferred
              }
              language: languageV2
              image {
                large
              }
            }
          }
        }
        studios {
          edges {
            isMain
            node {
              id
              name
            }
          }
        }
        reviewPreview: reviews(perPage: 2, sort: [RATING_DESC, ID]) {
          pageInfo {
            total
          }
          nodes {
            id
            summary
            rating
            ratingAmount
            user {
              id
              name
              avatar {
                large
              }
            }
          }
        }
        recommendations(perPage: 7, sort: [RATING_DESC, ID]) {
          pageInfo {
            total
          }
          nodes {
            id
            rating
            userRating
            mediaRecommendation {
              id
              title {
                userPreferred
              }
              format
              type
              status(version: 2)
              bannerImage
              coverImage {
                large
              }
            }
            user {
              id
              name
              avatar {
                large
              }
            }
          }
        }
        externalLinks {
          id
          site
          url
          type
          language
          color
          icon
          notes
          isDisabled
        }
        streamingEpisodes {
          site
          title
          thumbnail
          url
        }
        trailer {
          id
          site
        }
        rankings {
          id
          rank
          type
          format
          year
          season
          allTime
          context
        }
        tags {
          id
          name
          description
          rank
          isMediaSpoiler
          isGeneralSpoiler
          userId
        }
        mediaListEntry {
          id
          status
          score
        }
        stats {
          statusDistribution {
            status
            amount
          }
          scoreDistribution {
            score
            amount
          }
        }
      }
    }
    """

    # GraphQL query for searching media with pagination
    MEDIA_SEARCH_QUERY = """
    query ($page: Int = 1, $perPage: Int = 20, $search: String, $type: MediaType, $format: [MediaFormat], $status: MediaStatus, $season: MediaSeason, $seasonYear: Int, $year: String, $onList: Boolean, $isAdult: Boolean = false, $genre: [String], $tag: [String] ) {
      Page(page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
          perPage
        }
        media(search: $search, type: $type, format_in: $format, status: $status, season: $season, seasonYear: $seasonYear, startDate_like: $year, onList: $onList, isAdult: $isAdult, genre_in: $genre, tag_in: $tag) {
          id
          title {
            userPreferred
            romaji
            english
            native
          }
          coverImage {
            large
            medium
            color
          }
          bannerImage
          startDate {
            year
            month
            day
          }
          endDate {
            year
            month
            day
          }
          description
          season
          seasonYear
          type
          format
          status(version: 2)
          episodes
          duration
          chapters
          volumes
          genres
          synonyms
          source(version: 3)
          isAdult
          meanScore
          averageScore
          popularity
          favourites
          hashtag
          countryOfOrigin
          isLicensed
          nextAiringEpisode {
            airingAt
            timeUntilAiring
            episode
          }
          studios {
            edges {
              isMain
              node {
                id
                name
              }
            }
          }
          tags {
            id
            name
            description
            rank
            isMediaSpoiler
            isGeneralSpoiler
          }
          trailer {
            id
            site
          }
        }
      }
    }
    """

    # Simple query for basic media information
    SIMPLE_MEDIA_QUERY = """
    query ($id: Int, $search: String, $type: MediaType) {
      Media(id: $id, search: $search, type: $type) {
        id
        title {
          userPreferred
          romaji
          english
          native
        }
        coverImage {
          large
          medium
        }
        bannerImage
        description
        type
        format
        status(version: 2)
        episodes
        duration
        chapters
        volumes
        genres
        meanScore
        averageScore
        popularity
        favourites
        season
        seasonYear
        startDate {
          year
          month
          day
        }
        endDate {
          year
          month
          day
        }
      }
    }
    """

    def __init__(self):
        """Initialize AniList service."""
        self.logger = get_logger(__name__)
        self.session: aiohttp.ClientSession | None = None

        # Rate limiting state
        self._rate_limit_remaining: int | None = None
        self._rate_limit_reset: int | None = None
        self._rate_limit_limit: int | None = None
        self._last_request_time: float | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _update_rate_limit_info(self, headers: dict[str, Any]) -> None:
        """Update rate limit information from response headers.

        Args:
            headers: Response headers containing rate limit info
        """
        if "X-RateLimit-Limit" in headers:
            self._rate_limit_limit = int(headers["X-RateLimit-Limit"])

        if "X-RateLimit-Remaining" in headers:
            self._rate_limit_remaining = int(headers["X-RateLimit-Remaining"])

        if "X-RateLimit-Reset" in headers:
            self._rate_limit_reset = int(headers["X-RateLimit-Reset"])

        self._last_request_time = time.time()

        self.logger.debug(
            "Rate limit info updated - Limit: %s, Remaining: %s, Reset: %s",
            self._rate_limit_limit,
            self._rate_limit_remaining,
            self._rate_limit_reset,
        )

    async def _wait_for_rate_limit_reset(self, retry_after: int | None = None) -> None:
        """Wait for rate limit to reset.

        Args:
            retry_after: Seconds to wait from Retry-After header, if available
        """
        if retry_after is not None:
            wait_time = retry_after
            self.logger.warning(
                "Rate limited by AniList API. Waiting %d seconds (from Retry-After header).",
                wait_time,
            )
        elif self._rate_limit_reset is not None:
            current_time = int(time.time())
            wait_time = max(0, self._rate_limit_reset - current_time)
            self.logger.warning(
                "Rate limited by AniList API. Waiting %d seconds until reset.",
                wait_time,
            )
        else:
            # Fallback to default wait time if no timing info available
            wait_time = 60  # Default 1 minute wait
            self.logger.warning(
                "Rate limited by AniList API. Waiting %d seconds (fallback).",
                wait_time,
            )

        if wait_time > 0:
            await asyncio.sleep(wait_time)

    def _raise_graphql_error(self, errors: list[dict[str, Any]]) -> None:
        """Raise a ValueError for GraphQL errors.

        Args:
            errors: List of GraphQL errors

        Raises:
            ValueError: Always raises with formatted GraphQL errors
        """
        error_msg = f"GraphQL errors: {errors}"
        raise ValueError(error_msg)

    async def _make_request(
        self, query: str, variables: dict[str, Any] | None = None, max_retries: int = 3
    ) -> dict[str, Any]:
        """Make a GraphQL request to AniList API with rate limiting and retry logic.

        Args:
            query: GraphQL query string
            variables: Query variables
            max_retries: Maximum number of retry attempts

        Returns:
            Response data

        Raises:
            aiohttp.ClientError: If request fails after all retries
            ValueError: If response contains errors
        """
        if not self.session:
            msg = "Service not initialized. Use async with statement."
            raise RuntimeError(msg)

        payload = {"query": query, "variables": variables or {}}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.logger.debug("Making AniList API request with variables: %s", variables)

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                # Check if we need to wait before making the request
                if (
                    self._rate_limit_remaining is not None
                    and self._rate_limit_remaining <= 1
                    and self._rate_limit_reset is not None
                ):
                    current_time = int(time.time())
                    if current_time < self._rate_limit_reset:
                        await self._wait_for_rate_limit_reset()

                async with self.session.post(
                    self.BASE_URL, json=payload, headers=headers
                ) as response:
                    self.logger.debug(
                        "AniList API response status: %s", response.status
                    )

                    # Update rate limit info from headers
                    self._update_rate_limit_info(response.headers)

                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = None
                        if "Retry-After" in response.headers:
                            retry_after = int(response.headers["Retry-After"])

                        self.logger.warning(
                            "Rate limited (attempt %d/%d). Status: %d",
                            attempt + 1,
                            max_retries + 1,
                            response.status,
                        )

                        if attempt < max_retries:
                            await self._wait_for_rate_limit_reset(retry_after)
                            continue
                        response.raise_for_status()  # Will raise ClientResponseError

                    # Handle other HTTP errors
                    response.raise_for_status()
                    data = await response.json()

                    if "errors" in data:
                        self.logger.error(
                            "AniList API GraphQL errors: %s", data["errors"]
                        )
                        self.logger.debug("AniList API request payload: %s", payload)
                        # Don't retry on GraphQL errors as they're likely permanent
                        self._raise_graphql_error(data["errors"])

                    return data.get("data", {})

            except aiohttp.ClientResponseError as e:
                last_exception = e
                if e.status == 429:
                    # Already handled above, but just in case
                    if attempt < max_retries:
                        retry_after = None
                        if "Retry-After" in e.headers:
                            retry_after = int(e.headers["Retry-After"])
                        await self._wait_for_rate_limit_reset(retry_after)
                        continue
                else:
                    # Don't retry on other client errors (4xx) - return empty result instead of raising
                    self.logger.warning(
                        "AniList API request failed with status %d: %s. Returning empty result.",
                        e.status,
                        e.message,
                    )
                    self.logger.debug(
                        "AniList API request details - URL: %s, payload: %s",
                        self.BASE_URL,
                        payload,
                    )
                    return {}

            except (TimeoutError, aiohttp.ClientError) as e:
                last_exception = e
                if attempt < max_retries:
                    wait_time = min(2**attempt, 30)  # Exponential backoff, max 30s
                    self.logger.warning(
                        "Request failed (attempt %d/%d), retrying in %d seconds: %s",
                        attempt + 1,
                        max_retries + 1,
                        wait_time,
                        str(e),
                    )
                    await asyncio.sleep(wait_time)
                    continue
                # If all retries exhausted, return empty result instead of raising
                self.logger.warning(
                    "AniList API request failed after all retries: %s. Returning empty result.",
                    str(e),
                )
                self.logger.debug(
                    "AniList API request details - URL: %s, payload: %s",
                    self.BASE_URL,
                    payload,
                )
                return {}

            except (ValueError, TypeError, KeyError) as e:
                last_exception = e
                self.logger.warning(
                    "AniList API request failed with unexpected error: %s. Returning empty result.",
                    str(e),
                )
                self.logger.debug(
                    "AniList API request details - URL: %s, payload: %s",
                    self.BASE_URL,
                    payload,
                )
                return {}

        # If we get here, all retries failed - return empty result instead of raising
        if last_exception:
            self.logger.warning(
                "AniList API request failed after %d attempts: %s. Returning empty result.",
                max_retries + 1,
                str(last_exception),
            )
        else:
            self.logger.warning(
                "AniList API request failed after %d attempts. Returning empty result.",
                max_retries + 1,
            )
        return {}

    @cached(ttl=ServiceCacheConfig.ANILIST_MEDIA_TTL, key_prefix="anilist_media_by_id")
    async def get_media_by_id(
        self,
        media_id: int,
        media_type: MediaType | None = None,
        detailed: bool = True,
    ) -> Media | None:
        """Get media by ID.

        Args:
            media_id: AniList media ID
            media_type: Optional media type filter
            detailed: Whether to use detailed query (default: True)

        Returns:
            Media object or None if not found
        """
        with timed_operation(f"anilist_get_media_by_id({media_id})", self.logger):
            variables = MediaByIdVariables(id=media_id, type=media_type).model_dump(
                exclude_none=True
            )

            query = self.MEDIA_QUERY if detailed else self.SIMPLE_MEDIA_QUERY

            try:
                data = await self._make_request(query, variables)

                if not data.get("Media"):
                    self.logger.warning("No media found with ID: %s", media_id)
                    return None

                # Map GraphQL response to our model (Media -> media)
                response_data = {"media": data["Media"]}
                response = MediaResponse(**response_data)
                self.logger.info(
                    "Retrieved media: %s",
                    response.media.title.userPreferred if response.media else "Unknown",
                )

            except ValidationError:
                self.logger.warning(
                    "Failed to parse media response for ID %s. Returning None.",
                    media_id,
                )
                return None
            except (aiohttp.ClientError, ValueError, KeyError) as e:
                self.logger.warning(
                    "Failed to get media by ID %s: %s. Returning None.",
                    media_id,
                    str(e),
                )
                return None
            else:
                return response.media

    @cached(
        ttl=ServiceCacheConfig.ANILIST_SEARCH_TTL, key_prefix="anilist_search_media"
    )
    async def search_media(
        self,
        search: str | None = None,
        media_type: MediaType | None = None,
        page: int = 1,
        per_page: int = 20,
        alternative_titles: list[str] | None = None,
        **kwargs: str | int | bool | list[str] | None,
    ) -> PageResponse | None:
        """Search for media.

        Args:
            search: Search query
            media_type: Media type filter
            page: Page number
            per_page: Items per page
            **kwargs: Additional search parameters

        Returns:
            PageResponse with search results
        """
        with timed_operation(
            f"anilist_search_media('{search}', {media_type})", self.logger
        ):
            # Build variables from parameters
            variables = MediaSearchVariables(
                search=search,
                type=media_type,
                page=page,
                perPage=per_page,
                **kwargs,
            ).model_dump(exclude_none=True)

            self.logger.debug("AniList search variables: %s", variables)
            data = await self._make_request(self.MEDIA_SEARCH_QUERY, variables)

            if not data.get("Page"):
                self.logger.warning(
                    "No search results for query: '%s' (type: %s)",
                    search,
                    media_type,
                )
                return None

            response = MediaPageResponse(**data)
            result_count = len(response.Page.media) if response.Page.media else 0
            self.logger.info(
                "Found %d media results for search: '%s' (type: %s)",
                result_count,
                search,
                media_type,
            )
            if not response.Page.media and alternative_titles:
                alternative_title = alternative_titles[0]
                self.logger.warning(
                    "Empty media results for query: '%s' (type: %s) retrying with title %s and alternative titles %s",
                    search,
                    media_type,
                    alternative_title,
                    alternative_titles,
                )
                return await self.search_media(
                    search=alternative_title,
                    media_type=media_type,
                    page=page,
                    per_page=per_page,
                    alternative_titles=alternative_titles[1:],
                )
            return response.Page

    @cached(
        ttl=ServiceCacheConfig.ANILIST_TRENDING_TTL, key_prefix="anilist_trending_anime"
    )
    async def get_trending_anime(
        self,
        page: int = 1,
        per_page: int = 20,
        alternative_titles: list[str] | None = None,
    ) -> PageResponse | None:
        """Get trending anime.

        Args:
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with trending anime
        """
        return await self.search_media(
            media_type=MediaType.ANIME,
            page=page,
            per_page=per_page,
            sort=["TRENDING_DESC", "POPULARITY_DESC"],
            alternative_titles=alternative_titles,
        )

    @cached(
        ttl=ServiceCacheConfig.ANILIST_TRENDING_TTL, key_prefix="anilist_popular_anime"
    )
    async def get_popular_anime(
        self,
        page: int = 1,
        per_page: int = 20,
        alternative_titles: list[str] | None = None,
    ) -> PageResponse | None:
        """Get popular anime.

        Args:
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with popular anime
        """
        return await self.search_media(
            media_type=MediaType.ANIME,
            page=page,
            per_page=per_page,
            sort=["POPULARITY_DESC"],
            alternative_titles=alternative_titles,
        )

    async def get_top_rated_anime(
        self,
        page: int = 1,
        per_page: int = 20,
        alternative_titles: list[str] | None = None,
    ) -> PageResponse | None:
        """Get top rated anime.

        Args:
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with top rated anime
        """
        return await self.search_media(
            media_type=MediaType.ANIME,
            page=page,
            per_page=per_page,
            sort=["SCORE_DESC"],
            alternative_titles=alternative_titles,
        )

    async def get_seasonal_anime(
        self,
        season: str,
        year: int,
        page: int = 1,
        per_page: int = 20,
        alternative_titles: list[str] | None = None,
    ) -> PageResponse | None:
        """Get seasonal anime.

        Args:
            season: Season (WINTER, SPRING, SUMMER, FALL)
            year: Year
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with seasonal anime
        """
        return await self.search_media(
            media_type=MediaType.ANIME,
            season=season,
            seasonYear=year,
            page=page,
            per_page=per_page,
            sort=["POPULARITY_DESC"],
            alternative_titles=alternative_titles,
        )

    async def get_upcoming_anime(
        self,
        page: int = 1,
        per_page: int = 20,
        alternative_titles: list[str] | None = None,
    ) -> PageResponse | None:
        """Get upcoming anime.

        Args:
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with upcoming anime
        """
        return await self.search_media(
            media_type=MediaType.ANIME,
            status="NOT_YET_RELEASED",
            page=page,
            per_page=per_page,
            sort=["POPULARITY_DESC"],
            alternative_titles=alternative_titles,
        )

    @cached(
        ttl=ServiceCacheConfig.ANILIST_SEARCH_TTL, key_prefix="anilist_search_anime"
    )
    async def search_anime(
        self,
        query: str,
        alternative_titles: list[str] | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> PageResponse | None:
        """Search anime by title.

        Args:
            query: Search query
            alternative_titles: Alternative titles
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with search results
        """
        return await self.search_media(
            search=query,
            media_type=MediaType.ANIME,
            page=page,
            per_page=per_page,
            alternative_titles=alternative_titles,
        )

    async def search_manga(
        self,
        query: str,
        alternative_titles: list[str] | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> PageResponse | None:
        """Search manga by title.

        Args:
            query: Search query
            alternative_titles: Alternative titles
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with search results
        """
        return await self.search_media(
            search=query,
            media_type=MediaType.MANGA,
            page=page,
            per_page=per_page,
            alternative_titles=alternative_titles,
        )

    async def get_media_relations(self, media_id: int) -> Media | None:
        """Get media with its relations.

        Args:
            media_id: AniList media ID

        Returns:
            Media object with relations
        """
        return await self.get_media_by_id(media_id, detailed=True)

    async def get_media_characters(self, media_id: int) -> Media | None:
        """Get media with character information.

        Args:
            media_id: AniList media ID

        Returns:
            Media object with character data
        """
        return await self.get_media_by_id(media_id, detailed=True)

    async def get_media_staff(self, media_id: int) -> Media | None:
        """Get media with staff information.

        Args:
            media_id: AniList media ID

        Returns:
            Media object with staff data
        """
        return await self.get_media_by_id(media_id, detailed=True)
