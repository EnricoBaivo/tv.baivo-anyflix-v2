"""Metadata enrichment service for matching and enhancing anime data with AniList."""

import asyncio
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

from cachetools import TTLCache

from ..models.anilist import Media as AniListMedia
from ..models.anilist import MediaType
from ..models.base import SearchResult
from ..models.enhanced import (
    EnhancedMediaInfo,
    EnhancedSearchResult,
    EnhancedSeriesDetail,
    MetadataStats,
)
from ..services.anilist_service import AniListService
from ..utils.logging_config import get_logger, timed_operation


class MetadataEnrichmentService:
    """Service for enriching anime data with AniList metadata (ANIME only)."""

    def __init__(self, cache_maxsize: int = 1000, cache_ttl: int = 3600):
        """Initialize the metadata enrichment service.

        Args:
            cache_maxsize: Maximum number of items to cache (default: 1000)
            cache_ttl: Time-to-live for cache entries in seconds (default: 3600 = 1 hour)
        """
        self.logger = get_logger(__name__)
        self.anilist_service = AniListService()

        # Use TTLCache for automatic expiration and LRU eviction
        self.cache: TTLCache[str, Tuple[Optional[AniListMedia], float]] = TTLCache(
            maxsize=cache_maxsize, ttl=cache_ttl
        )

        self.stats = MetadataStats(
            total_requests=0,
            anilist_matches=0,
            match_rate=0.0,
            cache_hits=0,
            cache_misses=0,
        )

        self.logger.info(
            f"Initialized MetadataEnrichmentService with cache (maxsize={cache_maxsize}, ttl={cache_ttl}s)"
        )

    def _normalize_title(self, title: str) -> str:
        """Normalize anime title for better matching."""
        # Remove common prefixes/suffixes and normalize
        title = re.sub(r"\s*\(.*?\)\s*", "", title)  # Remove parentheses content
        title = re.sub(r"\s*\[.*?\]\s*", "", title)  # Remove bracket content
        title = re.sub(
            r"\s*-\s*(Staffel|Season|S)\s*\d+.*", "", title, flags=re.IGNORECASE
        )  # Remove season info
        title = re.sub(
            r"\s*-\s*(German|English|Dub|Sub).*", "", title, flags=re.IGNORECASE
        )  # Remove language info
        title = re.sub(r"\s+", " ", title).strip()  # Normalize whitespace
        return title

    def _calculate_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        # Normalize both titles
        norm1 = self._normalize_title(title1.lower())
        norm2 = self._normalize_title(title2.lower())

        # Direct match
        if norm1 == norm2:
            return 1.0

        # Sequence matching
        similarity = SequenceMatcher(None, norm1, norm2).ratio()

        # Bonus for partial matches
        if norm1 in norm2 or norm2 in norm1:
            similarity = max(similarity, 0.8)

        # Check for common alternative titles
        common_alternatives = {
            "shingeki no kyojin": "attack on titan",
            "kimetsu no yaiba": "demon slayer",
            "yakusoku no neverland": "the promised neverland",
            "boku no hero academia": "my hero academia",
        }

        for alt1, alt2 in common_alternatives.items():
            if (alt1 in norm1 and alt2 in norm2) or (alt2 in norm1 and alt1 in norm2):
                similarity = max(similarity, 0.9)

        return similarity

    async def _search_anilist_match(
        self, title: str
    ) -> Tuple[Optional[AniListMedia], float]:
        """Search for the best AniList match for a given title (ANIME only)."""
        try:
            # Search AniList for potential matches (anime only)
            search_results = await self.anilist_service.search_anime(title, per_page=10)

            if not search_results or not search_results.media:
                return None, 0.0

            best_match = None
            best_similarity = 0.0

            for anime in search_results.media:
                # Skip non-anime entries (extra safety check)
                if anime.type != MediaType.ANIME:
                    self.logger.debug(
                        f"Skipping non-anime entry: {anime.title.userPreferred if anime.title else 'Unknown'} (type: {anime.type})"
                    )
                    continue

                # Check all available titles
                titles_to_check = []
                if anime.title:
                    if anime.title.userPreferred:
                        titles_to_check.append(anime.title.userPreferred)
                    if anime.title.romaji:
                        titles_to_check.append(anime.title.romaji)
                    if anime.title.english:
                        titles_to_check.append(anime.title.english)
                    if anime.title.native:
                        titles_to_check.append(anime.title.native)

                # Add synonyms
                if anime.synonyms:
                    titles_to_check.extend(anime.synonyms)

                # Find best similarity
                for anilist_title in titles_to_check:
                    similarity = self._calculate_similarity(title, anilist_title)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = anime

            # Only return matches above threshold
            if best_similarity >= 0.7:
                self.logger.debug(
                    f"Found anime match: '{title}' -> '{best_match.title.userPreferred if best_match.title else 'Unknown'}' "
                    f"(confidence: {best_similarity:.2f}, type: {best_match.type})"
                )
                return best_match, best_similarity

            self.logger.debug(
                f"No suitable anime match found for '{title}' (best similarity: {best_similarity:.2f})"
            )
            return None, 0.0

        except Exception as e:
            self.logger.error(f"Error searching AniList for '{title}': {e}")
            return None, 0.0

    async def get_anilist_match(
        self, title: str
    ) -> Tuple[Optional[AniListMedia], float]:
        """Get AniList match for a title with caching."""
        cache_key = self._normalize_title(title.lower())

        # Check cache first
        if cache_key in self.cache:
            self.stats.cache_hits += 1
            return self.cache[cache_key]

        self.stats.cache_misses += 1

        # Search for match
        match, confidence = await self._search_anilist_match(title)

        # Cache result
        self.cache[cache_key] = (match, confidence)

        return match, confidence

    def _extract_enhanced_metadata(self, anilist_media: AniListMedia) -> Dict:
        """Extract enhanced metadata from AniList media."""
        metadata = {}

        if anilist_media.title and anilist_media.title.userPreferred:
            metadata["enhanced_title"] = anilist_media.title.userPreferred

        if anilist_media.description:
            # Clean HTML tags from description
            clean_desc = re.sub(r"<[^>]+>", "", anilist_media.description)
            metadata["enhanced_description"] = clean_desc

        if anilist_media.genres:
            metadata["enhanced_genres"] = anilist_media.genres

        if anilist_media.averageScore:
            metadata["score"] = anilist_media.averageScore

        if anilist_media.popularity:
            metadata["popularity"] = anilist_media.popularity

        if anilist_media.startDate and anilist_media.startDate.year:
            metadata["year"] = anilist_media.startDate.year

        if anilist_media.season:
            metadata["season"] = (
                anilist_media.season.value
                if hasattr(anilist_media.season, "value")
                else str(anilist_media.season)
            )

        if anilist_media.episodes:
            metadata["episode_count"] = anilist_media.episodes

        if anilist_media.status:
            metadata["status_text"] = (
                anilist_media.status.value
                if hasattr(anilist_media.status, "value")
                else str(anilist_media.status)
            )

        # Extract studios
        if anilist_media.studios and anilist_media.studios.edges:
            studios = []
            for edge in anilist_media.studios.edges:
                if edge.node and edge.node.name:
                    studios.append(edge.node.name)
            if studios:
                metadata["studios"] = studios

        # Extract external links
        if anilist_media.externalLinks:
            links = []
            for link in anilist_media.externalLinks:
                if link.url and link.site:
                    links.append(
                        {
                            "site": link.site,
                            "url": link.url,
                            "type": (
                                link.type.value
                                if link.type and hasattr(link.type, "value")
                                else None
                            ),
                        }
                    )
            if links:
                metadata["external_links"] = links

        # Extract characters (simplified)
        if anilist_media.characterPreview and anilist_media.characterPreview.edges:
            characters = []
            for edge in anilist_media.characterPreview.edges[:6]:  # Limit to 6
                if edge.node and edge.node.name:
                    char_info = {
                        "name": (
                            edge.node.name.userPreferred
                            if edge.node.name.userPreferred
                            else "Unknown"
                        ),
                        "role": (
                            edge.role.value
                            if edge.role and hasattr(edge.role, "value")
                            else None
                        ),
                    }
                    if edge.voiceActors:
                        voice_actors = []
                        for va in edge.voiceActors[:2]:  # Limit to 2 VAs
                            if va.name and va.name.userPreferred:
                                voice_actors.append(va.name.userPreferred)
                        if voice_actors:
                            char_info["voice_actors"] = voice_actors
                    characters.append(char_info)
            if characters:
                metadata["characters"] = characters

        # Extract staff (simplified)
        if anilist_media.staffPreview and anilist_media.staffPreview.edges:
            staff = []
            for edge in anilist_media.staffPreview.edges[:8]:  # Limit to 8
                if edge.node and edge.node.name:
                    staff.append(
                        {
                            "name": (
                                edge.node.name.userPreferred
                                if edge.node.name.userPreferred
                                else "Unknown"
                            ),
                            "role": edge.role if edge.role else "Unknown",
                        }
                    )
            if staff:
                metadata["staff"] = staff

        # Extract relations (simplified)
        if anilist_media.relations and anilist_media.relations.edges:
            relations = []
            for edge in anilist_media.relations.edges[:5]:  # Limit to 5
                if edge.node and edge.node.title:
                    relations.append(
                        {
                            "title": (
                                edge.node.title.userPreferred
                                if edge.node.title.userPreferred
                                else "Unknown"
                            ),
                            "type": (
                                edge.relationType.value
                                if edge.relationType
                                and hasattr(edge.relationType, "value")
                                else None
                            ),
                            "format": (
                                edge.node.format.value
                                if edge.node.format
                                and hasattr(edge.node.format, "value")
                                else None
                            ),
                        }
                    )
            if relations:
                metadata["relations"] = relations

        # Extract recommendations (simplified)
        if anilist_media.recommendations and anilist_media.recommendations.nodes:
            recommendations = []
            for rec in anilist_media.recommendations.nodes[:5]:  # Limit to 5
                if rec.mediaRecommendation and rec.mediaRecommendation.title:
                    recommendations.append(
                        {
                            "title": (
                                rec.mediaRecommendation.title.userPreferred
                                if rec.mediaRecommendation.title.userPreferred
                                else "Unknown"
                            ),
                            "rating": rec.rating,
                        }
                    )
            if recommendations:
                metadata["recommendations"] = recommendations

        # Extract tags (simplified)
        if anilist_media.tags:
            tags = []
            for tag in anilist_media.tags[:10]:  # Limit to 10
                if tag.name:
                    tag_info = {"name": tag.name}
                    if tag.description:
                        tag_info["description"] = tag.description
                    if tag.rank:
                        tag_info["rank"] = tag.rank
                    tags.append(tag_info)
            if tags:
                metadata["tags"] = tags

        return metadata

    async def enrich_search_result(self, result: SearchResult) -> EnhancedSearchResult:
        """Enrich a single search result with AniList metadata."""
        self.stats.total_requests += 1

        # Get AniList match
        anilist_match, confidence = await self.get_anilist_match(result.name)

        enhanced_result = EnhancedSearchResult(
            name=result.name,
            image_url=result.image_url,
            link=result.link,
            anilist_data=anilist_match,
            anilist_id=anilist_match.id if anilist_match else None,
            match_confidence=confidence if confidence > 0 else None,
        )

        if anilist_match:
            self.stats.anilist_matches += 1

        # Update match rate
        self.stats.match_rate = (
            self.stats.anilist_matches / self.stats.total_requests
        ) * 100

        return enhanced_result

    async def enrich_search_results(
        self, results: List[SearchResult], max_concurrent: int = 5
    ) -> List[EnhancedSearchResult]:
        """Enrich multiple search results with AniList metadata."""
        with timed_operation(
            f"enrich_search_results({len(results)} items)", self.logger
        ):
            # Process results in batches to avoid overwhelming AniList API
            semaphore = asyncio.Semaphore(max_concurrent)

            async def enrich_with_semaphore(result):
                async with semaphore:
                    return await self.enrich_search_result(result)

            tasks = [enrich_with_semaphore(result) for result in results]
            enhanced_results = await asyncio.gather(*tasks)

            self.logger.info(
                f"Enriched {len(enhanced_results)} results, {self.stats.anilist_matches} with AniList matches"
            )
            return enhanced_results

    async def enrich_media_info(
        self, name: str, original_data: dict
    ) -> EnhancedMediaInfo:
        """Enrich media info with AniList metadata."""
        self.stats.total_requests += 1

        # Get AniList match
        anilist_match, confidence = await self.get_anilist_match(name)

        # Start with original data
        enhanced_data = {
            "name": name,
            "image_url": original_data.get("image_url", ""),
            "description": original_data.get("description", ""),
            "author": original_data.get("author", ""),
            "status": original_data.get("status", 5),
            "genre": original_data.get("genre", []),
            "anilist_data": anilist_match,
            "anilist_id": anilist_match.id if anilist_match else None,
            "match_confidence": confidence if confidence > 0 else None,
        }

        # Add enhanced metadata if we have a match
        if anilist_match and confidence >= 0.7:
            enhanced_metadata = self._extract_enhanced_metadata(anilist_match)
            enhanced_data.update(enhanced_metadata)
            self.stats.anilist_matches += 1

        # Update match rate
        self.stats.match_rate = (
            self.stats.anilist_matches / self.stats.total_requests
        ) * 100

        return EnhancedMediaInfo(**enhanced_data)

    async def enrich_series_detail(
        self, slug: str, original_data: dict
    ) -> EnhancedSeriesDetail:
        """Enrich series detail with AniList metadata."""
        self.stats.total_requests += 1

        # Extract title from slug or use provided name
        title = original_data.get("name", slug.replace("-", " ").title())

        # Get AniList match
        anilist_match, confidence = await self.get_anilist_match(title)

        # Start with original data
        enhanced_data = {
            "slug": slug,
            "seasons": original_data.get("seasons", []),
            "movies": original_data.get("movies", []),
            "anilist_data": anilist_match,
            "anilist_id": anilist_match.id if anilist_match else None,
            "match_confidence": confidence if confidence > 0 else None,
        }

        # Add enhanced metadata if we have a match
        if anilist_match and confidence >= 0.7:
            enhanced_metadata = self._extract_enhanced_metadata(anilist_match)
            enhanced_data.update(enhanced_metadata)
            self.stats.anilist_matches += 1

        # Update match rate
        self.stats.match_rate = (
            self.stats.anilist_matches / self.stats.total_requests
        ) * 100

        return EnhancedSeriesDetail(**enhanced_data)

    def get_stats(self) -> MetadataStats:
        """Get current metadata enrichment statistics."""
        return self.stats

    def get_cache_info(self) -> Dict[str, any]:
        """Get cache information and statistics."""
        return {
            "cache_size": len(self.cache),
            "cache_maxsize": self.cache.maxsize,
            "cache_ttl": self.cache.ttl,
            "cache_hits": self.stats.cache_hits,
            "cache_misses": self.stats.cache_misses,
            "hit_rate": (
                self.stats.cache_hits
                / (self.stats.cache_hits + self.stats.cache_misses)
                if (self.stats.cache_hits + self.stats.cache_misses) > 0
                else 0.0
            ),
        }

    def clear_cache(self):
        """Clear the metadata cache."""
        cache_size = len(self.cache)
        self.cache.clear()
        self.logger.info(f"Metadata cache cleared ({cache_size} items removed)")

    def resize_cache(self, maxsize: int):
        """Resize the cache maximum size."""
        old_maxsize = self.cache.maxsize
        # Create new cache with new size and copy existing items
        old_cache = dict(self.cache)
        self.cache = TTLCache(maxsize=maxsize, ttl=self.cache.ttl)

        # Copy items back (TTLCache will handle size limit)
        for key, value in old_cache.items():
            self.cache[key] = value

        self.logger.info(f"Cache resized from {old_maxsize} to {maxsize} items")

    def set_cache_ttl(self, ttl: int):
        """Set new TTL for cache (affects new entries only)."""
        old_ttl = self.cache.ttl
        # Note: TTLCache doesn't allow changing TTL of existing cache
        # We need to create a new cache to change TTL
        old_cache = dict(self.cache)
        self.cache = TTLCache(maxsize=self.cache.maxsize, ttl=ttl)

        # Copy items back (they will use new TTL)
        for key, value in old_cache.items():
            self.cache[key] = value

        self.logger.info(f"Cache TTL changed from {old_ttl}s to {ttl}s")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.anilist_service.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.anilist_service.__aexit__(exc_type, exc_val, exc_tb)
