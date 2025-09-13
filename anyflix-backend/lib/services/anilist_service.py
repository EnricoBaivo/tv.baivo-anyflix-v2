"""AniList API service for GraphQL queries."""

import json
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import ValidationError

from ..models.anilist import (
    Media,
    MediaByIdVariables,
    MediaPageResponse,
    MediaResponse,
    MediaSearchVariables,
    MediaType,
    PageResponse,
)
from ..utils.caching import ServiceCacheConfig, cached
from ..utils.logging_config import get_logger, timed_operation


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
    query ($page: Int = 1, $perPage: Int = 20, $search: String, $type: MediaType, $format: [MediaFormat], $status: MediaStatus, $season: MediaSeason, $seasonYear: Int, $year: String, $onList: Boolean, $isAdult: Boolean = false, $genre: [String], $tag: [String], $sort: [MediaSort] = [POPULARITY_DESC, SCORE_DESC]) {
      Page(page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
          perPage
        }
        media(search: $search, type: $type, format_in: $format, status: $status, season: $season, seasonYear: $seasonYear, startDate_like: $year, onList: $onList, isAdult: $isAdult, genre_in: $genre, tag_in: $tag, sort: $sort) {
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
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _make_request(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a GraphQL request to AniList API.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Response data

        Raises:
            aiohttp.ClientError: If request fails
            ValueError: If response contains errors
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use async with statement.")

        payload = {"query": query, "variables": variables or {}}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.logger.debug(f"Making AniList API request with variables: {variables}")

        async with self.session.post(
            self.BASE_URL, json=payload, headers=headers
        ) as response:
            response.raise_for_status()
            data = await response.json()

            if "errors" in data:
                error_msg = f"GraphQL errors: {data['errors']}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            return data.get("data", {})

    @cached(ttl=ServiceCacheConfig.ANILIST_MEDIA_TTL, key_prefix="anilist_media_by_id")
    async def get_media_by_id(
        self,
        media_id: int,
        media_type: Optional[MediaType] = None,
        detailed: bool = True,
    ) -> Optional[Media]:
        """Get media by ID.

        Args:
            media_id: AniList media ID
            media_type: Optional media type filter
            detailed: Whether to use detailed query (default: True)

        Returns:
            Media object or None if not found
        """
        with timed_operation(f"get_media_by_id({media_id})", self.logger):
            variables = MediaByIdVariables(id=media_id, type=media_type).model_dump(
                exclude_none=True
            )

            query = self.MEDIA_QUERY if detailed else self.SIMPLE_MEDIA_QUERY

            try:
                data = await self._make_request(query, variables)

                if not data.get("Media"):
                    self.logger.warning(f"No media found with ID: {media_id}")
                    return None

                # Map GraphQL response to our model (Media -> media)
                response_data = {"media": data["Media"]}
                response = MediaResponse(**response_data)
                self.logger.info(
                    f"Retrieved media: {response.media.title.userPreferred if response.media else 'Unknown'}"
                )
                return response.media

            except ValidationError as e:
                self.logger.error(f"Failed to parse media response: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Failed to get media by ID {media_id}: {e}")
                raise

    @cached(
        ttl=ServiceCacheConfig.ANILIST_SEARCH_TTL, key_prefix="anilist_search_media"
    )
    async def search_media(
        self,
        search: Optional[str] = None,
        media_type: Optional[MediaType] = None,
        page: int = 1,
        per_page: int = 20,
        **kwargs,
    ) -> Optional[PageResponse]:
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
        with timed_operation(f"search_media('{search}', {media_type})", self.logger):
            # Build variables from parameters
            variables = MediaSearchVariables(
                search=search, type=media_type, page=page, perPage=per_page, **kwargs
            ).model_dump(exclude_none=True)

            try:
                data = await self._make_request(self.MEDIA_SEARCH_QUERY, variables)

                if not data.get("Page"):
                    self.logger.warning(f"No search results for query: {search}")
                    return None

                response = MediaPageResponse(**data)
                result_count = len(response.Page.media) if response.Page.media else 0
                self.logger.info(
                    f"Found {result_count} media results for search: '{search}'"
                )
                return response.Page

            except ValidationError as e:
                self.logger.error(f"Failed to parse search response: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Failed to search media: {e}")
                raise

    @cached(
        ttl=ServiceCacheConfig.ANILIST_TRENDING_TTL, key_prefix="anilist_trending_anime"
    )
    async def get_trending_anime(
        self, page: int = 1, per_page: int = 20
    ) -> Optional[PageResponse]:
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
        )

    @cached(
        ttl=ServiceCacheConfig.ANILIST_TRENDING_TTL, key_prefix="anilist_popular_anime"
    )
    async def get_popular_anime(
        self, page: int = 1, per_page: int = 20
    ) -> Optional[PageResponse]:
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
        )

    async def get_top_rated_anime(
        self, page: int = 1, per_page: int = 20
    ) -> Optional[PageResponse]:
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
        )

    async def get_seasonal_anime(
        self, season: str, year: int, page: int = 1, per_page: int = 20
    ) -> Optional[PageResponse]:
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
        )

    async def get_upcoming_anime(
        self, page: int = 1, per_page: int = 20
    ) -> Optional[PageResponse]:
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
        )

    @cached(
        ttl=ServiceCacheConfig.ANILIST_SEARCH_TTL, key_prefix="anilist_search_anime"
    )
    async def search_anime(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> Optional[PageResponse]:
        """Search anime by title.

        Args:
            query: Search query
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with search results
        """
        return await self.search_media(
            search=query, media_type=MediaType.ANIME, page=page, per_page=per_page
        )

    async def search_manga(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> Optional[PageResponse]:
        """Search manga by title.

        Args:
            query: Search query
            page: Page number
            per_page: Items per page

        Returns:
            PageResponse with search results
        """
        return await self.search_media(
            search=query, media_type=MediaType.MANGA, page=page, per_page=per_page
        )

    async def get_media_relations(self, media_id: int) -> Optional[Media]:
        """Get media with its relations.

        Args:
            media_id: AniList media ID

        Returns:
            Media object with relations
        """
        return await self.get_media_by_id(media_id, detailed=True)

    async def get_media_characters(self, media_id: int) -> Optional[Media]:
        """Get media with character information.

        Args:
            media_id: AniList media ID

        Returns:
            Media object with character data
        """
        return await self.get_media_by_id(media_id, detailed=True)

    async def get_media_staff(self, media_id: int) -> Optional[Media]:
        """Get media with staff information.

        Args:
            media_id: AniList media ID

        Returns:
            Media object with staff data
        """
        return await self.get_media_by_id(media_id, detailed=True)
