#!/usr/bin/env python3
"""
Demo script for BULLET/BULLET anime fetching from AniWorld with metadata enrichment.

This script demonstrates:
1. Fetching anime details from AniWorld provider
2. Getting episodes and video sources
3. Enriching metadata with AniList service
4. Enriching metadata with TMDB service
5. Displaying combined results
"""

import asyncio
import os
import sys

from lib.services.anilist_service import AniListService
from lib.services.matching_service import MatchingService

# Add the lib directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from lib.providers.aniworld import AniWorldProvider
from lib.providers.serienstream import SerienStreamProvider
from lib.services.tmdb_service import TMDBService


async def simple_test() -> None:
    """Main demo function."""
    print("🚀 BULLET/BULLET Anime Demo - Fetching from Multiple Sources")
    print("=" * 80)

    # AniWorld URL for BULLET/BULLET
    aniworld_url = "/anime/stream/bulletbullet"
    serienstream_url = "/serie/stream/alien-earth"
    aniworld_search_query = "BULLET/BULLET"
    serienstream_search_query = "Alien Earth"
    async with AniWorldProvider() as provider:
        # Get anime details
        aniworld_media_info = await provider.get_detail(url=aniworld_url)
        # print(media_info.model_dump_json(indent=2))
    async with SerienStreamProvider() as provider:
        # Get anime details
        serienstream_media_info = await provider.get_detail(url=serienstream_url)
        # print(media_info.model_dump_json(indent=2))

    async with AniListService() as anilist_service:
        anilist_media_info = await anilist_service.search_anime(
            query=aniworld_search_query
        )
        for media in anilist_media_info.media:
            print(media.title.userPreferred)
    print("=" * 80)
    print("TMDB Media Info")
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    if not tmdb_api_key:
        msg = "TMDB_API_KEY environment variable is required"
        raise ValueError(msg)

    async with TMDBService(tmdb_api_key) as tmdb_service:
        tmdb_media_info = await tmdb_service.search_multi(
            query=serienstream_search_query
        )
        animie_tmdb_media_info = await tmdb_service.search_multi(
            query=aniworld_search_query
        )
        for media in tmdb_media_info.results:
            print(media.name if media.name else media.title)
    print("=" * 80)
    print("TMDB Media Info")
    best_match, confidence = MatchingService.calculate_match_confidence(
        serienstream_media_info, tmdb_media_info
    )
    print(f"Confidence: {confidence}")
    if best_match:
        match_name = (
            best_match.name if hasattr(best_match, "name") else best_match.title
        )
        print(f"Best match: {match_name}")
        # Print TMDB URL
        if hasattr(best_match, "media_type"):
            if best_match.media_type == "movie":
                print(f"TMDB URL: https://www.themoviedb.org/movie/{best_match.id}")
            elif best_match.media_type == "tv":
                print(f"TMDB URL: https://www.themoviedb.org/tv/{best_match.id}")
    else:
        print("No match found")
    print("=" * 80)
    print("AniWorld Media Info")
    print(f"best match for {aniworld_media_info.name}")
    best_match, confidence = MatchingService.calculate_match_confidence(
        aniworld_media_info, animie_tmdb_media_info
    )
    print(f"Confidence: {confidence}")
    if best_match:
        match_name = (
            best_match.name if hasattr(best_match, "name") else best_match.title
        )
        print(f"Best match: {match_name}")
        # Print TMDB URL
        if hasattr(best_match, "media_type"):
            if best_match.media_type == "movie":
                print(f"TMDB URL: https://www.themoviedb.org/movie/{best_match.id}")
            elif best_match.media_type == "tv":
                print(f"TMDB URL: https://www.themoviedb.org/tv/{best_match.id}")
    else:
        print("No match found")
    print("=" * 80)
    # Calculate confidence against AniList PageResponse
    best_match, confidence = MatchingService.calculate_match_confidence(
        aniworld_media_info, anilist_media_info
    )
    print(f"Confidence: {confidence}")
    if best_match:
        # Safe access to title with proper type checking
        if best_match.title and hasattr(best_match.title, "userPreferred"):
            print(f"Best match: {best_match.title.userPreferred}")
        else:
            print(f"Best match: {getattr(best_match, 'name', 'Unknown')}")
        # Print AniList URL
        print(f"AniList URL: https://anilist.co/anime/{best_match.id}")
    else:
        print("No match found")
    print("=" * 80)

    print("=" * 80)
    print("SerienStream Media Info")
    best_match, confidence = MatchingService.calculate_match_confidence(
        serienstream_media_info, anilist_media_info
    )
    print(f"Confidence: {confidence}")
    if best_match:
        # Safe access to title with proper type checking
        if best_match.title and hasattr(best_match.title, "userPreferred"):
            print(f"Best match: {best_match.title.userPreferred}")
        else:
            print(f"Best match: {getattr(best_match, 'name', 'Unknown')}")
        # Print AniList URL
        print(f"AniList URL: https://anilist.co/anime/{best_match.id}")
    else:
        print("No match found")
    print("=" * 80)


async def test_popular_anime() -> None:
    """Test popular anime."""
    async with AniWorldProvider() as aniworld_provider:
        popular_anime = await aniworld_provider.get_popular()
        print(popular_anime.model_dump_json(indent=2))


async def main() -> None:
    """Main function."""
    await test_popular_anime()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
