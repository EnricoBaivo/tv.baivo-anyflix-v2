"""Unified Series Enrichment Service - consolidates provider data and TMDB enrichment."""

import logging

import httpx

from lib.models.base import (
    EnrichedEpisode,
    EnrichedSeason,
    EnrichedSeriesDetail,
    Episode,
    MediaInfo,
    Season,
    SeriesDetail,
)
from lib.models.tmdb import (
    TMDBEpisodeDetail,
    TMDBSeasonDetail,
    TMDBTVDetail,
)
from lib.providers.base import BaseProvider
from lib.services.series_converter import SeriesConverterService
from lib.services.tmdb_enrichment_service import TMDBEnrichmentService

logger = logging.getLogger(__name__)


class EnrichedSeriesData:
    """Container for enriched series data with all TMDB details."""

    def __init__(
        self,
        series_detail: SeriesDetail,
        tmdb_tv_detail: TMDBTVDetail | None,
        match_confidence: float | None,
    ):
        """Initialize enriched series data container.

        Args:
            series_detail: Hierarchical series structure (base, not enriched)
            tmdb_tv_detail: Full TMDB TV details
            match_confidence: Match confidence score
        """
        self.series_detail = series_detail
        self.tmdb_tv_detail = tmdb_tv_detail
        self.match_confidence = match_confidence

    @property
    def tmdb_id(self) -> int | None:
        """Get TMDB TV show ID if available."""
        return self.tmdb_tv_detail.id if self.tmdb_tv_detail else None


class SeriesEnrichmentService:
    """Unified service for fetching and enriching series data.

    This service combines provider data fetching, TMDB enrichment, and
    hierarchical conversion into a single, efficient workflow. It eliminates
    code duplication across router endpoints.
    """

    def __init__(self, tmdb_enrichment_service: TMDBEnrichmentService) -> None:
        """Initialize the series enrichment service.

        Args:
            tmdb_enrichment_service: TMDB enrichment service instance
        """
        self.tmdb_enrichment = tmdb_enrichment_service

    async def fetch_and_enrich_series(
        self,
        provider: BaseProvider,
        url: str,
        slug: str | None = None,
        fetch_episodes: bool = True,
    ) -> EnrichedSeriesData:
        """Fetch series from provider and enrich with basic TMDB data.

        This is the core method that handles the common workflow:
        1. Fetch from provider
        2. Get basic TMDB TV show details
        3. Convert to hierarchical structure

        Args:
            provider: Provider instance to fetch from
            url: Series URL
            slug: Optional slug override
            fetch_episodes: Whether to fetch full episode list

        Returns:
            EnrichedSeriesData with series structure and TMDB details

        Raises:
            httpx.HTTPError: If provider request fails
            ValueError: If data processing fails
        """
        # Step 1: Fetch from provider
        detail_response = await provider.get_detail(url, episodes=fetch_episodes)

        # Step 2: Enrich with TMDB (basic TV info)
        tmdb_match, tmdb_detail, match_confidence = (
            await self.tmdb_enrichment.enrich_media_info(detail_response)
        )

        # Step 3: Convert to hierarchical structure
        if not slug:
            slug = url.split("/")[-1] if "/" in url else "unknown"

        series_detail = SeriesConverterService.convert_to_hierarchical(
            detail_response, slug=slug
        )

        # Extract TMDBTVDetail for TV shows
        tmdb_tv_detail = None
        if isinstance(tmdb_detail, TMDBTVDetail):
            tmdb_tv_detail = tmdb_detail

        return EnrichedSeriesData(
            series_detail=series_detail,
            tmdb_tv_detail=tmdb_tv_detail,
            match_confidence=match_confidence,
        )

    async def build_enriched_seasons(
        self,
        series_detail: SeriesDetail,
        tmdb_id: int | None,
        tmdb_tv_detail: TMDBTVDetail | None = None,
    ) -> list[EnrichedSeason]:
        """Build enriched seasons with TMDB data.

        Converts base Seasons to EnrichedSeasons and fetches TMDB season
        data for each season.

        Args:
            series_detail: Base series detail with seasons
            tmdb_id: TMDB TV show ID (if available)
            tmdb_tv_detail: Optional pre-fetched TV detail for episode counts

        Returns:
            List of EnrichedSeason with embedded TMDB data
        """
        enriched_seasons: list[EnrichedSeason] = []

        for season in series_detail.seasons:
            # Convert base episodes to enriched episodes
            enriched_episodes = [
                EnrichedEpisode(
                    season=ep.season,
                    episode=ep.episode,
                    kind=ep.kind,
                    number=ep.number,
                    title=ep.title,
                    name=ep.name,
                    url=ep.url,
                    tags=ep.tags or [],
                    tmdb_episode_data=None,  # Will be enriched later if needed
                )
                for ep in season.episodes
            ]

            # Get episode count from TMDB TV detail if available
            episode_count = None
            if tmdb_tv_detail and tmdb_tv_detail.seasons:
                for tmdb_season in tmdb_tv_detail.seasons:
                    if tmdb_season.season_number == season.season:
                        episode_count = tmdb_season.episode_count
                        break

            # Create enriched season (TMDB season data fetched on demand)
            enriched_season = EnrichedSeason(
                season=season.season,
                title=season.title,
                episodes=enriched_episodes,
                tmdb_season_data=None,  # Fetched on demand
                episode_count=episode_count,
            )
            enriched_seasons.append(enriched_season)

        return enriched_seasons

    async def enrich_season_with_tmdb(
        self,
        season: Season,
        tmdb_id: int,
        season_number: int,
    ) -> tuple[EnrichedSeason, TMDBSeasonDetail | None]:
        """Enrich a single season with full TMDB season data.

        Fetches TMDB season details and merges episode metadata into the
        enriched season episodes.

        Args:
            season: Provider season to enrich
            tmdb_id: TMDB TV show ID
            season_number: Season number to fetch from TMDB

        Returns:
            Tuple of (enriched_season, tmdb_season_detail)
        """
        # Fetch TMDB season details
        tmdb_season = await self.tmdb_enrichment.enrich_season(tmdb_id, season_number)

        # Create TMDB episode lookup map
        tmdb_episodes_map: dict[int, TMDBEpisodeDetail] = {}
        if tmdb_season and tmdb_season.episodes:
            # Convert TMDBEpisode to TMDBEpisodeDetail-like object
            for tmdb_ep in tmdb_season.episodes:
                # Create a simplified TMDBEpisodeDetail from TMDBEpisode
                episode_detail = TMDBEpisodeDetail(
                    id=tmdb_ep.id,
                    name=tmdb_ep.name,
                    overview=tmdb_ep.overview,
                    season_number=tmdb_ep.season_number,
                    episode_number=tmdb_ep.episode_number,
                    episode_type=tmdb_ep.episode_type,
                    production_code=tmdb_ep.production_code,
                    air_date=tmdb_ep.air_date,
                    still_path=tmdb_ep.still_path,
                    runtime=tmdb_ep.runtime,
                    vote_average=tmdb_ep.vote_average,
                    vote_count=tmdb_ep.vote_count,
                )
                tmdb_episodes_map[tmdb_ep.episode_number] = episode_detail

        # Create enriched episodes with TMDB data
        enriched_episodes: list[EnrichedEpisode] = []
        for episode in season.episodes:
            tmdb_episode_data = None
            if episode.episode is not None:
                tmdb_episode_data = tmdb_episodes_map.get(episode.episode)

            enriched_episode = EnrichedEpisode(
                season=episode.season,
                episode=episode.episode,
                kind=episode.kind,
                number=episode.number,
                title=episode.title,
                name=episode.name,
                url=episode.url,
                tags=episode.tags or [],
                tmdb_episode_data=tmdb_episode_data,
            )
            enriched_episodes.append(enriched_episode)

        # Get episode count from TMDB season
        episode_count = len(tmdb_season.episodes) if tmdb_season else None

        # Create enriched season
        enriched_season = EnrichedSeason(
            season=season.season,
            title=season.title,
            episodes=enriched_episodes,
            tmdb_season_data=tmdb_season,
            episode_count=episode_count,
        )

        return enriched_season, tmdb_season

    async def enrich_all_seasons_with_tmdb(
        self,
        seasons: list[Season],
        tmdb_id: int,
    ) -> list[EnrichedSeason]:
        """Enrich all seasons with TMDB season data.

        Efficiently fetches TMDB data for each season and merges episode
        metadata. Continues on error for individual seasons.

        Args:
            seasons: List of provider seasons to enrich
            tmdb_id: TMDB TV show ID

        Returns:
            List of enriched seasons with TMDB episode metadata
        """
        enriched_seasons: list[EnrichedSeason] = []

        for season in seasons:
            try:
                enriched_season, _ = await self.enrich_season_with_tmdb(
                    season, tmdb_id, season.season
                )
                enriched_seasons.append(enriched_season)
            except (httpx.HTTPError, ValueError, RuntimeError):
                logger.exception(
                    "Failed to enrich season %d with TMDB data, using provider data only",
                    season.season,
                )
                # Convert to enriched season without TMDB data
                enriched_episodes = [
                    EnrichedEpisode(
                        season=ep.season,
                        episode=ep.episode,
                        kind=ep.kind,
                        number=ep.number,
                        title=ep.title,
                        name=ep.name,
                        url=ep.url,
                        tags=ep.tags or [],
                        tmdb_episode_data=None,
                    )
                    for ep in season.episodes
                ]
                enriched_seasons.append(
                    EnrichedSeason(
                        season=season.season,
                        title=season.title,
                        episodes=enriched_episodes,
                        tmdb_season_data=None,
                        episode_count=None,
                    )
                )

        return enriched_seasons

    async def get_enriched_episode(
        self,
        episode: Episode,
        tmdb_id: int,
        season_number: int,
        episode_number: int,
    ) -> EnrichedEpisode:
        """Get enriched episode with full TMDB episode details.

        Fetches TMDB episode data with videos, images, crew, and guest_stars.

        Args:
            episode: Base episode from provider
            tmdb_id: TMDB TV show ID
            season_number: Season number
            episode_number: Episode number

        Returns:
            EnrichedEpisode with tmdb_episode_data
        """
        tmdb_episode_data = await self.tmdb_enrichment.enrich_episode(
            tmdb_id, season_number, episode_number
        )

        return EnrichedEpisode(
            season=episode.season,
            episode=episode.episode,
            kind=episode.kind,
            number=episode.number,
            title=episode.title,
            name=episode.name,
            url=episode.url,
            tags=episode.tags or [],
            tmdb_episode_data=tmdb_episode_data,
        )

    def find_season(
        self, series_detail: SeriesDetail, season_number: int
    ) -> Season | None:
        """Find a season by number in series detail.

        Args:
            series_detail: Series detail to search
            season_number: Season number to find

        Returns:
            Season if found, None otherwise
        """
        for season in series_detail.seasons:
            if season.season == season_number:
                return season
        return None

    def find_episode(self, season: Season, episode_number: int) -> Episode | None:
        """Find an episode by number in a season.

        Args:
            season: Season to search
            episode_number: Episode number to find

        Returns:
            Episode if found, None otherwise
        """
        for episode in season.episodes:
            if episode.episode == episode_number:
                return episode
        return None

    @staticmethod
    def convert_season_to_enriched(
        season: Season,
        tmdb_season_data: TMDBSeasonDetail | None = None,
    ) -> EnrichedSeason:
        """Convert a base Season to EnrichedSeason without TMDB episode enrichment.

        Args:
            season: Base season to convert
            tmdb_season_data: Optional TMDB season data

        Returns:
            EnrichedSeason with converted episodes
        """
        enriched_episodes = [
            EnrichedEpisode(
                season=ep.season,
                episode=ep.episode,
                kind=ep.kind,
                number=ep.number,
                title=ep.title,
                name=ep.name,
                url=ep.url,
                tags=ep.tags or [],
                tmdb_episode_data=None,
            )
            for ep in season.episodes
        ]

        episode_count = (
            len(tmdb_season_data.episodes) if tmdb_season_data else None
        )

        return EnrichedSeason(
            season=season.season,
            title=season.title,
            episodes=enriched_episodes,
            tmdb_season_data=tmdb_season_data,
            episode_count=episode_count,
        )

    @staticmethod
    def convert_episode_to_enriched(
        episode: Episode,
        tmdb_episode_data: TMDBEpisodeDetail | None = None,
    ) -> EnrichedEpisode:
        """Convert a base Episode to EnrichedEpisode.

        Args:
            episode: Base episode to convert
            tmdb_episode_data: Optional TMDB episode data

        Returns:
            EnrichedEpisode with TMDB data if provided
        """
        return EnrichedEpisode(
            season=episode.season,
            episode=episode.episode,
            kind=episode.kind,
            number=episode.number,
            title=episode.title,
            name=episode.name,
            url=episode.url,
            tags=episode.tags or [],
            tmdb_episode_data=tmdb_episode_data,
        )
