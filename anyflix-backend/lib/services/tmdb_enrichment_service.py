"""TMDB Enrichment Service for enriching provider data with TMDB metadata."""

import logging

from lib.models.base import MediaInfo
from lib.models.tmdb import (
    TMDBEpisodeDetail,
    TMDBMovieDetail,
    TMDBSearchResult,
    TMDBSeasonDetail,
    TMDBTVDetail,
)
from lib.services.matching_service import MatchingService
from lib.services.tmdb_service import TMDBService

logger = logging.getLogger(__name__)


class TMDBEnrichmentService:
    """Service for enriching provider data with TMDB metadata.

    Maintains clean separation between data fetching (providers) and
    data enrichment (TMDB). Used at the router level to enrich
    MediaInfo with TMDB details.
    """

    def __init__(self, tmdb_service: TMDBService) -> None:
        """Initialize the enrichment service.

        Args:
            tmdb_service: The TMDB service instance for API calls
        """
        self.tmdb_service = tmdb_service

    async def enrich_media_info(
        self, media_info: MediaInfo
    ) -> tuple[TMDBSearchResult | None, TMDBTVDetail | TMDBMovieDetail | None, float]:
        """Enrich MediaInfo with TMDB data.

        Uses a priority-based lookup strategy:
        1. If imdb_id is present, use direct lookup (100% confidence)
        2. Otherwise, use fuzzy search with matching service

        Args:
            media_info: The MediaInfo to enrich with TMDB data

        Returns:
            Tuple of (search_result, detail, confidence)
            - search_result: The matched TMDB search result
            - detail: Full TMDB details (TMDBTVDetail or TMDBMovieDetail)
            - confidence: 1.0 for IMDb lookup, variable for fuzzy match
        """
        # Priority 1: Direct IMDb lookup (100% confidence)
        if media_info.imdb_id:
            logger.info(
                "Using IMDb ID lookup for '%s' with ID: %s",
                media_info.name,
                media_info.imdb_id,
            )
            result = await self.tmdb_service.find_by_external_id(
                media_info.imdb_id, "imdb_id"
            )
            if result.results:
                match = result.results[0]
                logger.info(
                    "Found direct IMDb match: %s (type: %s)",
                    match.title or match.name,
                    match.media_type,
                )
                detail = await self._fetch_detail(match)
                return match, detail, 1.0
            logger.warning(
                "No TMDB result found for IMDb ID: %s, falling back to search",
                media_info.imdb_id,
            )

        # Priority 2: Fuzzy search with matching service
        logger.info("Using fuzzy search for '%s'", media_info.name)
        search_result = await self.tmdb_service.search_multi(media_info.name)
        best_match, confidence = MatchingService.calculate_match_confidence(
            media_info, search_result
        )

        if best_match:
            logger.info(
                "Found fuzzy match: %s (confidence: %.2f)",
                best_match.title or best_match.name,
                confidence,
            )
            detail = await self._fetch_detail(best_match)
            return best_match, detail, confidence

        logger.warning("No TMDB match found for '%s'", media_info.name)
        return None, None, 0.0

    async def _fetch_detail(
        self, match: TMDBSearchResult
    ) -> TMDBTVDetail | TMDBMovieDetail | None:
        """Fetch full details for a matched result.

        Args:
            match: The TMDB search result to fetch details for

        Returns:
            TMDBTVDetail for TV shows, TMDBMovieDetail for movies, or None
        """
        if match.media_type == "tv":
            logger.debug("Fetching TV details for ID: %d", match.id)
            return await self.tmdb_service.get_tv_details(
                match.id, append_to_response="external_ids,images,videos"
            )
        if match.media_type == "movie":
            logger.debug("Fetching movie details for ID: %d", match.id)
            return await self.tmdb_service.get_details(
                match.id, append_to_response="external_ids,images,videos"
            )
        logger.warning("Unknown media type: %s", match.media_type)
        return None

    async def enrich_season(
        self, tv_id: int, season_number: int
    ) -> TMDBSeasonDetail | None:
        """Enrich a specific season with TMDB data.

        API: GET /tv/{series_id}/season/{season_number}
        Docs: https://developer.themoviedb.org/reference/tv-season-details

        Args:
            tv_id: TMDB TV show ID
            season_number: Season number to fetch

        Returns:
            TMDBSeasonDetail with episodes, videos, and images or None
        """
        logger.info("Fetching season %d details for TV ID: %d", season_number, tv_id)
        season_detail = await self.tmdb_service.get_tv_season_details(
            tv_id, season_number
        )
        if season_detail:
            logger.info(
                "Found season %d with %d episodes",
                season_number,
                len(season_detail.episodes),
            )
        else:
            logger.warning(
                "No TMDB season data found for TV ID %d, season %d",
                tv_id,
                season_number,
            )
        return season_detail

    async def enrich_episode(
        self, tv_id: int, season_number: int, episode_number: int
    ) -> TMDBEpisodeDetail | None:
        """Enrich a specific episode with TMDB data.

        API: GET /tv/{series_id}/season/{season_number}/episode/{episode_number}
        Docs: https://developer.themoviedb.org/reference/tv-episode-details

        Args:
            tv_id: TMDB TV show ID
            season_number: Season number
            episode_number: Episode number

        Returns:
            TMDBEpisodeDetail with videos and images or None
        """
        logger.info(
            "Fetching S%dE%d details for TV ID: %d",
            season_number,
            episode_number,
            tv_id,
        )
        episode_detail = await self.tmdb_service.get_tv_episode_details(
            tv_id, season_number, episode_number
        )
        if episode_detail:
            logger.info(
                "Found episode: %s (S%dE%d)",
                episode_detail.name,
                season_number,
                episode_number,
            )
        else:
            logger.warning(
                "No TMDB episode data found for TV ID %d, S%dE%d",
                tv_id,
                season_number,
                episode_number,
            )
        return episode_detail

