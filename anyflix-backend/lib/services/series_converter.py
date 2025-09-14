"""Series conversion service for transforming flat episode data into hierarchical structure."""

import logging
import re
from collections import defaultdict

from lib.models.base import Episode, MediaInfo, Movie, MovieKind, Season, SeriesDetail

logger = logging.getLogger(__name__)


class SeriesConverterService:
    """Service for converting flat episode data to hierarchical series structure."""

    @staticmethod
    def convert_to_hierarchical(
        detail_response: MediaInfo, slug: str | None = None
    ) -> SeriesDetail:
        """Convert flat MediaInfo to hierarchical SeriesDetail structure.

        Args:
            detail_response: MediaInfo with flat episode data
            slug: Optional slug override, if not provided will extract from URL

        Returns:
            SeriesDetail with episodes organized by seasons and movies

        Raises:
            ValueError: If episode data is invalid or cannot be processed
        """
        if not slug:
            slug = SeriesConverterService._extract_slug(detail_response.episodes)

        # Organize episodes by season and movies
        seasons_dict: dict[int, list[Episode]] = defaultdict(list)
        movies_list: list[Movie] = []

        for episode in detail_response.episodes:
            if not episode.title or not episode.url:
                continue

            # Check if this is a movie/film
            movie = SeriesConverterService._try_parse_as_movie(episode)
            if movie:
                movies_list.append(movie)
                continue

            # Parse as regular episode
            parsed_episode = SeriesConverterService._parse_episode(episode)
            if parsed_episode and parsed_episode.season is not None:
                seasons_dict[parsed_episode.season].append(parsed_episode)

        # Create Season objects
        seasons = []
        for season_num in sorted(seasons_dict.keys()):
            episodes = sorted(seasons_dict[season_num], key=lambda e: e.episode or 0)
            season_title = f"Staffel {season_num}"
            seasons.append(
                Season(season=season_num, title=season_title, episodes=episodes)
            )

        # Sort movies by number
        movies_list.sort(key=lambda m: m.number)

        return SeriesDetail(slug=slug, seasons=seasons, movies=movies_list)

    @staticmethod
    def _extract_slug(episodes: list[Episode]) -> str:
        """Extract slug from episode URLs."""
        for episode in episodes:
            if episode.url:
                # Extract from URL pattern like /anime/stream/attack-on-titan/staffel-4/episode-30
                match = re.search(r"/anime/stream/([^/]+)/", episode.url)
                if match:
                    return match.group(1)
        return "unknown"

    @staticmethod
    def _parse_episode(episode: Episode) -> Episode | None:
        """Parse episode information, creating a clean Episode object without nulls."""
        # Try to extract season/episode from title first
        season_num, episode_num, clean_title = (
            SeriesConverterService._parse_episode_title(episode.title)
        )

        # Fallback to URL parsing if title parsing failed
        if season_num is None or episode_num is None:
            url_season, url_episode = SeriesConverterService._parse_episode_url(
                episode.url
            )
            season_num = season_num or url_season
            episode_num = episode_num or url_episode

        if season_num is None or episode_num is None:
            return None

        # Create clean episode object with only necessary fields
        return Episode(
            season=season_num,
            episode=episode_num,
            title=clean_title or episode.title,
            url=episode.url,
            tags=episode.tags if episode.tags else [],
        )

    @staticmethod
    def _parse_episode_title(title: str) -> tuple[int | None, int | None, str | None]:
        """Parse German episode format: 'Staffel X Folge Y : Title [Tags]'."""
        episode_pattern = r"^Staffel\s*(?P<season>\d+)\s*Folge\s*(?P<episode>\d+)\s*:\s*(?P<title>.+)$"
        match = re.match(episode_pattern, title.strip())

        if match:
            season = int(match.group("season"))
            episode = int(match.group("episode"))
            clean_title = match.group("title").strip()

            # Remove tags from title
            clean_title = re.sub(r"\[([^\]]+)\]", "", clean_title).strip()

            return season, episode, clean_title

        return None, None, None

    @staticmethod
    def _parse_episode_url(url: str) -> tuple[int | None, int | None]:
        """Extract season and episode numbers from URL."""
        url_match = re.search(r"/staffel-(?P<season>\d+)/episode-(?P<episode>\d+)", url)
        if url_match:
            return int(url_match.group("season")), int(url_match.group("episode"))
        return None, None

    @staticmethod
    def _try_parse_as_movie(episode: Episode) -> Movie | None:
        """Try to parse episode as a movie/film."""
        # Check for German film format: 'Film X : Title [Kind]'
        film_pattern = r"^Film\s*(?P<num>\d+)\s*:\s*(?P<title>.+?)(?:\s*\[(?P<kind>OVA|Movie)\])?\s*$"
        match = re.match(film_pattern, episode.title.strip(), re.IGNORECASE)

        if match:
            number = int(match.group("num"))
            title = match.group("title").strip()
            kind_str = match.group("kind")

            # Determine movie kind
            if kind_str:
                if kind_str.lower() == "ova":
                    kind = MovieKind.OVA
                elif kind_str.lower() == "movie":
                    kind = MovieKind.MOVIE
                else:
                    kind = MovieKind.SPECIAL
            elif "/filme/" in episode.url:
                kind = MovieKind.MOVIE
            else:
                kind = MovieKind.SPECIAL

            # Remove additional tags from title
            title = re.sub(r"\[([^\]]+)\]", "", title).strip()

            return Movie(
                number=number,
                title=title,
                kind=kind,
                url=episode.url,
                tags=episode.tags if episode.tags else [],
            )

        return None
