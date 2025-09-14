"""Service for calculating match confidence between search queries and results."""

import contextlib
import logging
import re
from difflib import SequenceMatcher

from lib.models.anilist import Media, PageResponse
from lib.models.base import MediaInfo
from lib.models.tmdb import (
    TMDBSearchResponse,
    TMDBSearchResult,
)

logger = logging.getLogger(__name__)


class MatchingService:
    """Service for calculating match confidence between search queries and external API results."""

    # Configuration constants for bonus weights
    GENRE_BONUS_WEIGHT = 0.15  # Up to 15% bonus for genre alignment
    YEAR_BONUS_WEIGHT = 0.10  # Up to 10% bonus for year proximity
    COUNTRY_BONUS_WEIGHT = 0.10  # Up to 10% bonus for country match
    POPULARITY_BONUS_WEIGHT = 0.10  # Up to 10% bonus for popularity
    RATING_BONUS_WEIGHT = 0.05  # Up to 5% bonus for ratings

    @staticmethod
    def calculate_match_confidence(
        source_data: MediaInfo,
        target_data_list: PageResponse | TMDBSearchResponse,
    ) -> tuple[Media | TMDBSearchResult | None, float]:
        """Calculate match confidence between source MediaInfo and target data.

        Args:
            source_data: MediaInfo object containing source media information
            target_data_list: Target data (PageResponse or TMDBSearchResponse)

        Returns:
            Tuple of (best_match_media, confidence_score)
            confidence_score is between 0.0 and 1.0
        """
        if isinstance(target_data_list, PageResponse):
            # Find best match in AniList PageResponse
            anilist_match, confidence = (
                MatchingService.find_best_anilist_match_from_media_info(
                    source_data, target_data_list
                )
            )
            return anilist_match, confidence
        if isinstance(target_data_list, TMDBSearchResponse):
            # Find best match in TMDB search response
            tmdb_match, confidence = (
                MatchingService._find_best_tmdb_match_from_media_info(
                    source_data, target_data_list
                )
            )
            return tmdb_match, confidence
        logger.warning("Unsupported target_data_list type: %s", type(target_data_list))
        return None, 0.0

    @staticmethod
    def find_best_anilist_match_from_media_info(
        source_data: MediaInfo, anilist_response: PageResponse
    ) -> tuple[Media | None, float]:
        """Find the best matching Media from AniList PageResponse.

        Args:
            source_data: Source MediaInfo to match against
            anilist_response: AniList PageResponse containing Media objects

        Returns:
            Tuple of (best_match_media, confidence_score)
        """
        if not anilist_response.media:
            return None, 0.0

        best_match = None
        best_confidence = 0.0

        for media in anilist_response.media:
            confidence = MatchingService._calculate_anilist_media_confidence(
                source_data, media
            )

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = media

        return best_match, best_confidence

    @staticmethod
    def _find_best_tmdb_match_from_media_info(
        source_data: MediaInfo, tmdb_response: TMDBSearchResponse
    ) -> tuple[TMDBSearchResult | None, float]:
        """Find the best matching result from TMDB SearchResponse.

        Args:
            source_data: Source MediaInfo to match against
            tmdb_response: TMDB SearchResponse containing results

        Returns:
            Tuple of (best_match_result, confidence_score)
        """
        if not tmdb_response.results:
            return None, 0.0

        best_match = None
        best_confidence = 0.0

        for result in tmdb_response.results:
            # Skip person results - we only want movies and TV shows
            if hasattr(result, "media_type") and result.media_type == "person":
                continue

            confidence = MatchingService._calculate_tmdb_result_confidence(
                source_data, result
            )

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = result

        return best_match, best_confidence

    @staticmethod
    def _calculate_anilist_media_confidence(
        source_data: MediaInfo, anilist_media: Media
    ) -> float:
        """Calculate confidence score between MediaInfo and AniList Media.

        Args:
            source_data: Source MediaInfo
            anilist_media: AniList Media object

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base title matching
        base_confidence = MatchingService._calculate_title_similarity(
            source_data, anilist_media
        )

        # Apply metadata bonuses
        genre_bonus = MatchingService._calculate_genre_bonus_anilist(
            source_data.genres, anilist_media.genres or []
        )

        year_bonus = MatchingService._calculate_year_bonus(
            source_data.start_year,
            anilist_media.startDate.year if anilist_media.startDate else None,
        )

        country_bonus = MatchingService._calculate_country_bonus(
            source_data.country_of_origin, anilist_media.countryOfOrigin
        )

        popularity_bonus = MatchingService._calculate_popularity_bonus_anilist(
            anilist_media.popularity
        )

        rating_bonus = MatchingService._calculate_rating_bonus_anilist(
            anilist_media.averageScore
        )

        # Combine base confidence with bonuses
        total_confidence = (
            base_confidence
            + genre_bonus
            + year_bonus
            + country_bonus
            + popularity_bonus
            + rating_bonus
        )

        # Ensure score stays within 0.0-1.0 range
        return min(1.0, max(0.0, total_confidence))

    @staticmethod
    def _calculate_tmdb_result_confidence(
        source_data: MediaInfo, tmdb_result: TMDBSearchResult
    ) -> float:
        """Calculate confidence score between MediaInfo and TMDB result.

        Args:
            source_data: Source MediaInfo
            tmdb_result: TMDB search result

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base title matching
        base_confidence = MatchingService._calculate_title_similarity_tmdb(
            source_data, tmdb_result
        )

        # Apply metadata bonuses
        genre_bonus = MatchingService._calculate_genre_bonus_tmdb(
            source_data.genres, getattr(tmdb_result, "genre_ids", [])
        )

        # Extract year from TMDB result
        tmdb_year = None
        if hasattr(tmdb_result, "release_date") and tmdb_result.release_date:
            with contextlib.suppress(ValueError, AttributeError):
                tmdb_year = int(tmdb_result.release_date.split("-")[0])
        elif hasattr(tmdb_result, "first_air_date") and tmdb_result.first_air_date:
            with contextlib.suppress(ValueError, AttributeError):
                tmdb_year = int(tmdb_result.first_air_date.split("-")[0])

        year_bonus = MatchingService._calculate_year_bonus(
            source_data.start_year, tmdb_year
        )

        # TMDB doesn't have country in search results, so skip country bonus
        country_bonus = 0.0

        popularity_bonus = MatchingService._calculate_popularity_bonus_tmdb(
            getattr(tmdb_result, "popularity", None)
        )

        rating_bonus = MatchingService._calculate_rating_bonus_tmdb(
            getattr(tmdb_result, "vote_average", None)
        )

        # Combine base confidence with bonuses
        total_confidence = (
            base_confidence
            + genre_bonus
            + year_bonus
            + country_bonus
            + popularity_bonus
            + rating_bonus
        )

        # Ensure score stays within 0.0-1.0 range
        return min(1.0, max(0.0, total_confidence))

    @staticmethod
    def _calculate_title_similarity(
        source_data: MediaInfo, anilist_media: Media
    ) -> float:
        """Calculate title similarity between MediaInfo and AniList Media.

        Args:
            source_data: Source MediaInfo
            anilist_media: AniList Media object

        Returns:
            Base confidence score from title matching
        """
        source_titles = MatchingService._normalize_titles(
            [source_data.name, *source_data.alternative_titles]
        )

        # Get all available titles from AniList media
        target_titles = []
        if anilist_media.title:
            if anilist_media.title.userPreferred:
                target_titles.append(anilist_media.title.userPreferred)
            if anilist_media.title.romaji:
                target_titles.append(anilist_media.title.romaji)
            if anilist_media.title.english:
                target_titles.append(anilist_media.title.english)
            if anilist_media.title.native:
                target_titles.append(anilist_media.title.native)

        # Add synonyms if available
        if anilist_media.synonyms:
            target_titles.extend(anilist_media.synonyms)

        target_titles = MatchingService._normalize_titles(target_titles)

        # Calculate best similarity score
        max_similarity = 0.0
        for source_title in source_titles:
            for target_title in target_titles:
                similarity = SequenceMatcher(None, source_title, target_title).ratio()
                max_similarity = max(max_similarity, similarity)

        return max_similarity

    @staticmethod
    def _calculate_title_similarity_tmdb(
        source_data: MediaInfo, tmdb_result: TMDBSearchResult
    ) -> float:
        """Calculate title similarity between MediaInfo and TMDB result.

        Args:
            source_data: Source MediaInfo
            tmdb_result: TMDB search result

        Returns:
            Base confidence score from title matching
        """
        source_titles = MatchingService._normalize_titles(
            [source_data.name, *source_data.alternative_titles]
        )

        # Get available titles from TMDB result
        target_titles = []
        if hasattr(tmdb_result, "title") and tmdb_result.title:
            target_titles.append(tmdb_result.title)
        if hasattr(tmdb_result, "name") and tmdb_result.name:
            target_titles.append(tmdb_result.name)
        if hasattr(tmdb_result, "original_title") and tmdb_result.original_title:
            target_titles.append(tmdb_result.original_title)
        if hasattr(tmdb_result, "original_name") and tmdb_result.original_name:
            target_titles.append(tmdb_result.original_name)

        target_titles = MatchingService._normalize_titles(target_titles)

        # Calculate best similarity score
        max_similarity = 0.0
        for source_title in source_titles:
            for target_title in target_titles:
                similarity = SequenceMatcher(None, source_title, target_title).ratio()
                max_similarity = max(max_similarity, similarity)

        return max_similarity

    @staticmethod
    def _normalize_titles(titles: list[str]) -> list[str]:
        """Normalize titles for better matching.

        Args:
            titles: List of title strings

        Returns:
            List of normalized title strings
        """
        normalized = []
        for title in titles:
            if not title:
                continue

            # Convert to lowercase and remove extra whitespace
            normalized_title = re.sub(r"\s+", " ", title.lower().strip())

            # Remove common punctuation and special characters
            normalized_title = re.sub(r"[^\w\s]", "", normalized_title)

            # Remove common stop words that might cause false negatives
            stop_words = [
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
            ]
            words = normalized_title.split()
            filtered_words = [w for w in words if w not in stop_words]

            if filtered_words:  # Only add if we have words left after filtering
                normalized.append(" ".join(filtered_words))
            else:  # Fallback to original if all words were stop words
                normalized.append(normalized_title)

        return normalized

    @staticmethod
    def _calculate_genre_bonus_anilist(
        source_genres: list[str], target_genres: list[str]
    ) -> float:
        """Calculate genre matching bonus for AniList data.

        Args:
            source_genres: Source genre list
            target_genres: Target genre list

        Returns:
            Bonus score (0.0 to GENRE_BONUS_WEIGHT)
        """
        if not source_genres or not target_genres:
            return 0.0

        # Normalize genres for comparison
        source_normalized = {genre.lower().strip() for genre in source_genres}
        target_normalized = {genre.lower().strip() for genre in target_genres}

        # Calculate intersection ratio
        intersection = source_normalized.intersection(target_normalized)
        union = source_normalized.union(target_normalized)

        if not union:
            return 0.0

        similarity_ratio = len(intersection) / len(union)
        return similarity_ratio * MatchingService.GENRE_BONUS_WEIGHT

    @staticmethod
    def _calculate_genre_bonus_tmdb(
        source_genres: list[str], target_genre_ids: list[int]
    ) -> float:
        """Calculate genre matching bonus for TMDB data.

        Args:
            source_genres: Source genre list
            target_genre_ids: Target genre ID list

        Returns:
            Bonus score (0.0 to GENRE_BONUS_WEIGHT)
        """
        # TMDB genre ID to name mapping (common genres)
        tmdb_genre_map = {
            28: "action",
            16: "animation",
            35: "comedy",
            80: "crime",
            99: "documentary",
            18: "drama",
            10751: "family",
            14: "fantasy",
            36: "history",
            27: "horror",
            10402: "music",
            9648: "mystery",
            10749: "romance",
            878: "science fiction",
            10770: "tv movie",
            53: "thriller",
            10752: "war",
            37: "western",
            12: "adventure",
            10759: "action & adventure",
            10762: "kids",
            10763: "news",
            10764: "reality",
            10765: "sci-fi & fantasy",
            10766: "soap",
            10767: "talk",
            10768: "war & politics",
        }

        if not source_genres or not target_genre_ids:
            return 0.0

        # Convert TMDB genre IDs to names
        target_genres = []
        for genre_id in target_genre_ids:
            if genre_id in tmdb_genre_map:
                target_genres.append(tmdb_genre_map[genre_id])

        # Use the same logic as AniList genre bonus
        return MatchingService._calculate_genre_bonus_anilist(
            source_genres, target_genres
        )

    @staticmethod
    def _calculate_year_bonus(
        source_year: int | None, target_year: int | None
    ) -> float:
        """Calculate year proximity bonus.

        Args:
            source_year: Source release year
            target_year: Target release year

        Returns:
            Bonus score (0.0 to YEAR_BONUS_WEIGHT)
        """
        if not source_year or not target_year:
            return 0.0

        year_diff = abs(source_year - target_year)

        # Full bonus for exact match, decreasing bonus for nearby years
        if year_diff == 0:
            return MatchingService.YEAR_BONUS_WEIGHT
        if year_diff == 1:
            return MatchingService.YEAR_BONUS_WEIGHT * 0.8
        if year_diff == 2:
            return MatchingService.YEAR_BONUS_WEIGHT * 0.5
        if year_diff <= 5:
            return MatchingService.YEAR_BONUS_WEIGHT * 0.2
        return 0.0

    @staticmethod
    def _calculate_country_bonus(
        source_country: str | None, target_country: str | None
    ) -> float:
        """Calculate country of origin bonus.

        Args:
            source_country: Source country
            target_country: Target country

        Returns:
            Bonus score (0.0 to COUNTRY_BONUS_WEIGHT)
        """
        if not source_country or not target_country:
            return 0.0

        # Normalize country names for comparison
        source_normalized = source_country.lower().strip()
        target_normalized = target_country.lower().strip()

        if source_normalized == target_normalized:
            return MatchingService.COUNTRY_BONUS_WEIGHT

        # Handle common country code variations
        country_aliases = {
            "japan": ["jp", "jpn", "japanese"],
            "united states": ["us", "usa", "american"],
            "united kingdom": ["uk", "gb", "british"],
            "south korea": ["kr", "kor", "korean"],
            "china": ["cn", "chn", "chinese"],
        }

        for country, aliases in country_aliases.items():
            if (
                (source_normalized == country and target_normalized in aliases)
                or (target_normalized == country and source_normalized in aliases)
                or (source_normalized in aliases and target_normalized in aliases)
            ):
                return MatchingService.COUNTRY_BONUS_WEIGHT

        return 0.0

    @staticmethod
    def _calculate_popularity_bonus_anilist(popularity: int | None) -> float:
        """Calculate popularity bonus for AniList data.

        Args:
            popularity: AniList popularity score

        Returns:
            Bonus score (0.0 to POPULARITY_BONUS_WEIGHT)
        """
        if not popularity:
            return 0.0

        # AniList popularity is typically 0-10000+
        # Give higher bonus to more popular content
        if popularity >= 5000:
            return MatchingService.POPULARITY_BONUS_WEIGHT
        if popularity >= 2000:
            return MatchingService.POPULARITY_BONUS_WEIGHT * 0.7
        if popularity >= 1000:
            return MatchingService.POPULARITY_BONUS_WEIGHT * 0.4
        if popularity >= 500:
            return MatchingService.POPULARITY_BONUS_WEIGHT * 0.2
        return 0.0

    @staticmethod
    def _calculate_popularity_bonus_tmdb(popularity: float | None) -> float:
        """Calculate popularity bonus for TMDB data.

        Args:
            popularity: TMDB popularity score

        Returns:
            Bonus score (0.0 to POPULARITY_BONUS_WEIGHT)
        """
        if not popularity:
            return 0.0

        # TMDB popularity is typically 0-1000+
        if popularity >= 100:
            return MatchingService.POPULARITY_BONUS_WEIGHT
        if popularity >= 50:
            return MatchingService.POPULARITY_BONUS_WEIGHT * 0.7
        if popularity >= 20:
            return MatchingService.POPULARITY_BONUS_WEIGHT * 0.4
        if popularity >= 10:
            return MatchingService.POPULARITY_BONUS_WEIGHT * 0.2
        return 0.0

    @staticmethod
    def _calculate_rating_bonus_anilist(average_score: int | None) -> float:
        """Calculate rating bonus for AniList data.

        Args:
            average_score: AniList average score (0-100)

        Returns:
            Bonus score (0.0 to RATING_BONUS_WEIGHT)
        """
        if not average_score:
            return 0.0

        # AniList scores are 0-100
        if average_score >= 80:
            return MatchingService.RATING_BONUS_WEIGHT
        if average_score >= 70:
            return MatchingService.RATING_BONUS_WEIGHT * 0.7
        if average_score >= 60:
            return MatchingService.RATING_BONUS_WEIGHT * 0.4
        return 0.0

    @staticmethod
    def _calculate_rating_bonus_tmdb(vote_average: float | None) -> float:
        """Calculate rating bonus for TMDB data.

        Args:
            vote_average: TMDB vote average (0-10)

        Returns:
            Bonus score (0.0 to RATING_BONUS_WEIGHT)
        """
        if not vote_average:
            return 0.0

        # TMDB scores are 0-10
        if vote_average >= 8.0:
            return MatchingService.RATING_BONUS_WEIGHT
        if vote_average >= 7.0:
            return MatchingService.RATING_BONUS_WEIGHT * 0.7
        if vote_average >= 6.0:
            return MatchingService.RATING_BONUS_WEIGHT * 0.4
        return 0.0
