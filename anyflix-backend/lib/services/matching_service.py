"""Service for calculating match confidence between search queries and results."""

import logging
import re
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

from ..models.anilist import Media, PageResponse
from ..models.tmdb import TMDBMovieDetail, TMDBTVDetail

logger = logging.getLogger(__name__)


class MatchingService:
    """Service for calculating match confidence between search queries and external API results."""

    @staticmethod
    def find_best_anilist_match(
        query: str, page_response: Optional[PageResponse]
    ) -> Tuple[Optional[Media], float]:
        """Find the best AniList match and calculate confidence.

        Args:
            query: Original search query
            page_response: AniList PageResponse with search results

        Returns:
            Tuple of (best_match_media, confidence_score)
            confidence_score is between 0.0 and 1.0
        """
        if not page_response or not page_response.media:
            return None, 0.0

        best_match = None
        best_score = 0.0

        for media in page_response.media:
            score = MatchingService._calculate_anilist_confidence(query, media)
            if score > best_score:
                best_score = score
                best_match = media

        return best_match, best_score

    @staticmethod
    def calculate_tmdb_confidence(
        query: str, tmdb_result: Optional[TMDBMovieDetail | TMDBTVDetail]
    ) -> float:
        """Calculate confidence for TMDB search result.

        Args:
            query: Original search query
            tmdb_result: TMDB result (movie or TV show)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not tmdb_result:
            return 0.0

        return MatchingService._calculate_tmdb_confidence(query, tmdb_result)

    @staticmethod
    def _calculate_anilist_confidence(query: str, media: Media) -> float:
        """Calculate confidence score for AniList media match.

        Args:
            query: Original search query
            media: AniList Media object

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not media.title:
            return 0.0

        query_clean = MatchingService._normalize_title(query)
        scores = []

        # Check different title variants
        title_variants = [
            media.title.userPreferred,
            media.title.romaji,
            media.title.english,
            media.title.native,
        ]

        for title in title_variants:
            if title:
                title_clean = MatchingService._normalize_title(title)
                score = MatchingService._calculate_string_similarity(
                    query_clean, title_clean
                )
                scores.append(score)

        # Check synonyms
        if media.synonyms:
            for synonym in media.synonyms:
                if synonym:
                    synonym_clean = MatchingService._normalize_title(synonym)
                    score = MatchingService._calculate_string_similarity(
                        query_clean, synonym_clean
                    )
                    scores.append(score)

        if not scores:
            return 0.0

        # Use the highest score
        base_score = max(scores)

        # Apply popularity bonus (small boost for popular titles)
        popularity_bonus = 0.0
        if media.popularity and media.popularity > 1000:
            popularity_bonus = min(0.1, media.popularity / 100000)  # Max 10% bonus

        # Apply score bonus (small boost for highly rated titles)
        score_bonus = 0.0
        if media.averageScore and media.averageScore > 70:
            score_bonus = min(0.05, (media.averageScore - 70) / 600)  # Max 5% bonus

        final_score = min(1.0, base_score + popularity_bonus + score_bonus)
        return final_score

    @staticmethod
    def _calculate_tmdb_confidence(
        query: str, tmdb_result: TMDBMovieDetail | TMDBTVDetail
    ) -> float:
        """Calculate confidence score for TMDB result match.

        Args:
            query: Original search query
            tmdb_result: TMDB movie or TV show result

        Returns:
            Confidence score between 0.0 and 1.0
        """
        query_clean = MatchingService._normalize_title(query)
        scores = []

        # Get title based on type
        if isinstance(tmdb_result, TMDBMovieDetail):
            title = tmdb_result.title
            original_title = tmdb_result.original_title
        else:  # TMDBTVDetail
            title = tmdb_result.name
            original_title = tmdb_result.original_name

        # Check main title
        if title:
            title_clean = MatchingService._normalize_title(title)
            scores.append(
                MatchingService._calculate_string_similarity(query_clean, title_clean)
            )

        # Check original title
        if original_title and original_title != title:
            original_clean = MatchingService._normalize_title(original_title)
            scores.append(
                MatchingService._calculate_string_similarity(
                    query_clean, original_clean
                )
            )

        if not scores:
            return 0.0

        # Use the highest score
        base_score = max(scores)

        # Apply popularity bonus (small boost for popular titles)
        popularity_bonus = 0.0
        if tmdb_result.popularity and tmdb_result.popularity > 10:
            popularity_bonus = min(0.1, tmdb_result.popularity / 1000)  # Max 10% bonus

        # Apply vote average bonus (small boost for highly rated titles)
        vote_bonus = 0.0
        if tmdb_result.vote_average and tmdb_result.vote_average > 7.0:
            vote_bonus = min(
                0.05, (tmdb_result.vote_average - 7.0) / 60
            )  # Max 5% bonus

        final_score = min(1.0, base_score + popularity_bonus + vote_bonus)
        return final_score

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize title for comparison.

        Args:
            title: Title to normalize

        Returns:
            Normalized title
        """
        # Convert to lowercase
        normalized = title.lower().strip()

        # Remove common punctuation and special characters
        normalized = re.sub(r"[^\w\s]", " ", normalized)

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()

        # Remove common words that don't affect matching
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
        words = normalized.split()
        words = [word for word in words if word not in stop_words]

        return " ".join(words)

    @staticmethod
    def _calculate_string_similarity(str1: str, str2: str) -> float:
        """Calculate similarity between two strings.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not str1 or not str2:
            return 0.0

        # Exact match gets perfect score
        if str1 == str2:
            return 1.0

        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, str1, str2).ratio()

        # Check if one string is contained in the other (partial match bonus)
        if str1 in str2 or str2 in str1:
            similarity = max(similarity, 0.8)  # Minimum 80% for substring matches

        return similarity
