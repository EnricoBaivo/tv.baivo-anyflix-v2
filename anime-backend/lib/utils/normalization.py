"""Series normalization utilities for transforming flat episodes into hierarchical structure."""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from ..models.base import Episode, LegacyEpisode, Movie, MovieKind, Season, SeriesDetail


def normalize_series_detail(
    flat_data: Dict, slug: Optional[str] = None
) -> SeriesDetail:
    """Normalize flat episodes data into hierarchical SeriesDetail structure.
    
    Args:
        flat_data: Dictionary with 'episodes' key containing list of LegacyEpisode-like dicts
        slug: Optional slug override, if not provided will try to extract from URLs
        
    Returns:
        SeriesDetail with episodes organized by seasons and movies
    """
    episodes_data = flat_data.get("episodes", [])
    if not slug:
        slug = _extract_slug_from_episodes(episodes_data)
    
    # Parse episodes into hierarchical structure
    seasons_dict: Dict[int, List[Episode]] = {}
    movies_list: List[Movie] = []
    
    for ep_data in episodes_data:
        name = ep_data.get("name", "")
        url = ep_data.get("url", "")
        date_upload = ep_data.get("date_upload")
        
        if not name or not url:
            continue
            
        # Try to parse as episode first
        episode_info = _parse_episode_name(name, url, date_upload)
        if episode_info:
            season_num = episode_info.season
            if season_num not in seasons_dict:
                seasons_dict[season_num] = []
            seasons_dict[season_num].append(episode_info)
            continue
            
        # Try to parse as movie/film
        movie_info = _parse_movie_name(name, url, date_upload)
        if movie_info:
            movies_list.append(movie_info)
    
    # Create Season objects
    seasons = []
    for season_num in sorted(seasons_dict.keys()):
        episodes = sorted(seasons_dict[season_num], key=lambda e: e.episode)
        season_title = f"Staffel {season_num}"
        seasons.append(Season(
            season=season_num,
            title=season_title,
            episodes=episodes
        ))
    
    # Sort movies by number
    movies_list.sort(key=lambda m: m.number)
    
    return SeriesDetail(
        slug=slug,
        seasons=seasons,
        movies=movies_list
    )


def _extract_slug_from_episodes(episodes_data: List[Dict]) -> str:
    """Extract slug from episode URLs."""
    for ep in episodes_data:
        url = ep.get("url", "")
        if url:
            # Extract from URL pattern like /anime/stream/attack-on-titan/staffel-4/episode-30
            match = re.search(r"/anime/stream/([^/]+)/", url)
            if match:
                return match.group(1)
    return "unknown"


def _parse_episode_name(name: str, url: str, date_upload: Optional[str]) -> Optional[Episode]:
    """Parse episode name using German format: 'Staffel X Folge Y : Title [Tags]'."""
    # Regex for German episode format
    episode_pattern = r"^Staffel\s*(?P<season>\d+)\s*Folge\s*(?P<episode>\d+)\s*:\s*(?P<title>.+)$"
    
    match = re.match(episode_pattern, name.strip())
    if not match:
        # Try URL fallback parsing
        url_match = re.search(r"/staffel-(?P<season>\d+)/episode-(?P<episode>\d+)", url)
        if url_match:
            # Extract title from name if possible
            title_match = re.search(r":\s*(.+)$", name)
            title = title_match.group(1).strip() if title_match else name.strip()
        else:
            return None
    else:
        url_match = match
        title = match.group("title").strip()
    
    season = int(url_match.group("season"))
    episode = int(url_match.group("episode"))
    
    # Extract tags from title (content in brackets)
    tags = []
    tag_pattern = r"\[([^\]]+)\]"
    tag_matches = re.findall(tag_pattern, title)
    if tag_matches:
        tags.extend(tag_matches)
        # Remove tags from title
        title = re.sub(tag_pattern, "", title).strip()
    
    return Episode(
        season=season,
        episode=episode,
        title=title,
        url=url,
        date_upload=date_upload,
        tags=tags
    )


def _parse_movie_name(name: str, url: str, date_upload: Optional[str]) -> Optional[Movie]:
    """Parse movie/film name using German format: 'Film X : Title [Kind]'."""
    # Regex for German film format - handle optional space before bracket
    film_pattern = r"^Film\s*(?P<num>\d+)\s*:\s*(?P<title>.+?)(?:\s*\[(?P<kind>OVA|Movie)\])?\s*$"
    
    match = re.match(film_pattern, name.strip(), re.IGNORECASE)
    if not match:
        # Try URL fallback parsing
        url_match = re.search(r"/filme/film-(?P<num>\d+)", url)
        if url_match:
            # Extract title from name if possible
            title_match = re.search(r":\s*(.+)$", name)
            title = title_match.group(1).strip() if title_match else name.strip()
            number = int(url_match.group("num"))
            kind_from_bracket = None
        else:
            return None
    else:
        number = int(match.group("num"))
        title = match.group("title").strip()
        kind_from_bracket = match.group("kind")
    
    # Determine movie kind
    if kind_from_bracket:
        if kind_from_bracket.lower() == "ova":
            kind = MovieKind.OVA
        elif kind_from_bracket.lower() == "movie":
            kind = MovieKind.MOVIE
        else:
            kind = MovieKind.SPECIAL
    elif "/filme/" in url:
        # Default to movie if in filme path
        kind = MovieKind.MOVIE
    else:
        kind = MovieKind.SPECIAL
    
    # Extract additional tags from title (content in brackets that isn't the kind)
    tags = []
    tag_pattern = r"\[([^\]]+)\]"
    tag_matches = re.findall(tag_pattern, title)
    if tag_matches:
        for tag in tag_matches:
            if tag.lower() not in ["ova", "movie"]:
                tags.append(tag)
        # Remove all tags from title
        title = re.sub(tag_pattern, "", title).strip()
    
    return Movie(
        number=number,
        title=title,
        kind=kind,
        url=url,
        date_upload=date_upload,
        tags=tags
    )


def series_detail_to_legacy_episodes(series_detail: SeriesDetail) -> List[LegacyEpisode]:
    """Convert SeriesDetail back to legacy flat episodes format for backward compatibility."""
    legacy_episodes = []
    
    # Convert seasons to legacy episodes
    for season in series_detail.seasons:
        for episode in season.episodes:
            # Reconstruct the legacy name format
            name = f"Staffel {episode.season} Folge {episode.episode} : {episode.title}"
            if episode.tags:
                name += f" [{']['.join(episode.tags)}]"
            
            legacy_episodes.append(LegacyEpisode(
                name=name,
                url=episode.url,
                date_upload=episode.date_upload
            ))
    
    # Convert movies to legacy episodes
    for movie in series_detail.movies:
        # Reconstruct the legacy name format
        name = f"Film {movie.number} : {movie.title}"
        if movie.kind == MovieKind.OVA:
            name += " [OVA]"
        elif movie.kind == MovieKind.MOVIE:
            name += " [Movie]"
        
        if movie.tags:
            name += f" [{']['.join(movie.tags)}]"
        
        legacy_episodes.append(LegacyEpisode(
            name=name,
            url=movie.url,
            date_upload=movie.date_upload
        ))
    
    return legacy_episodes
