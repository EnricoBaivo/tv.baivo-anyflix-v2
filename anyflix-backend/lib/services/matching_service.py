"""Service for calculating match confidence between search queries and results."""

import contextlib
import logging
import re
from difflib import SequenceMatcher

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
        target_data_list: TMDBSearchResponse,
    ) -> tuple[TMDBSearchResult | None, float]:
        """Calculate match confidence between source MediaInfo and target data.

        Args:
            source_data: MediaInfo object containing source media information
            target_data_list: Target data (TMDBSearchResponse)

        Returns:
            Tuple of (best_match_media, confidence_score)
            confidence_score is between 0.0 and 1.0
        """
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
        target_genres = [
            tmdb_genre_map[genre_id]
            for genre_id in target_genre_ids
            if genre_id in tmdb_genre_map
        ]

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
