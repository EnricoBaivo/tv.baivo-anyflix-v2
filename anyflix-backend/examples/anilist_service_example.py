#!/usr/bin/env python3
"""
AniList Service Usage Examples

This file demonstrates how to properly use the AniListService for various
anime metadata operations while respecting API rate limits.

Rate Limits (as of 2025):
- 30 requests per minute (degraded state)
- 90 requests per minute (normal state)
- Burst limiting also applies

Best Practices:
1. Always use async context managers
2. Handle rate limiting gracefully
3. Batch operations when possible
4. Cache results to avoid repeated calls

Usage: python examples/anilist_service_example.py (from project root)
"""

import asyncio
import json
import os
import sys
from typing import List, Optional

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.models.anilist import MediaType
from lib.services.anilist_service import AniListService


async def example_single_search():
    """Example: Search for a single anime by title."""
    print("🔍 Example 1: Single Anime Search")
    print("-" * 40)

    service = AniListService()

    try:
        async with service:
            # Search for a popular anime
            result = await service.search_anime("One Piece")

            if result and hasattr(result, "media") and result.media:
                first_anime = result.media[0]
                print(f"✅ Found: {first_anime.title.romaji}")
                print(f"📊 Score: {first_anime.averageScore}")
                print(f"📺 Episodes: {first_anime.episodes}")
                print(f"📅 Year: {first_anime.seasonYear}")

                # Convert to dict for JSON serialization
                anime_dict = (
                    first_anime.model_dump()
                    if hasattr(first_anime, "model_dump")
                    else first_anime.dict()
                )
                print(f"📋 Data structure keys: {list(anime_dict.keys())[:10]}...")
            else:
                print("❌ No results found")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


async def example_multiple_searches_with_delay():
    """Example: Multiple searches with rate limiting consideration."""
    print("🔍 Example 2: Multiple Searches with Rate Limiting")
    print("-" * 50)

    service = AniListService()
    search_terms = [
        "Attack on Titan",
        "Demon Slayer",
        "Jujutsu Kaisen",
        "My Hero Academia",
    ]

    results = []

    try:
        async with service:
            for i, term in enumerate(search_terms):
                print(f"🔍 Searching for: {term}")

                try:
                    result = await service.search_anime(term)

                    if result and hasattr(result, "media") and result.media:
                        anime = result.media[0]
                        anime_data = {
                            "title": anime.title.romaji,
                            "score": anime.averageScore,
                            "episodes": anime.episodes,
                            "year": anime.seasonYear,
                            "status": anime.status.value if anime.status else None,
                        }
                        results.append(anime_data)
                        print(
                            f"✅ Found: {anime_data['title']} ({anime_data['score']}/100)"
                        )
                    else:
                        print(f"❌ No results for: {term}")

                except Exception as search_error:
                    print(f"❌ Failed to search '{term}': {search_error}")

                    # If rate limited, wait before continuing
                    if "429" in str(search_error) or "Too Many Requests" in str(
                        search_error
                    ):
                        print("⏳ Rate limited - waiting 30 seconds...")
                        await asyncio.sleep(30)

                # Small delay between requests to be respectful
                if i < len(search_terms) - 1:
                    await asyncio.sleep(2)

    except Exception as e:
        print(f"❌ Service error: {e}")

    print(f"\n📊 Successfully retrieved {len(results)} anime:")
    for anime in results:
        print(f"  • {anime['title']} - {anime['score']}/100")

    print()


async def example_get_by_id():
    """Example: Get anime by specific AniList ID."""
    print("🔍 Example 3: Get Anime by ID")
    print("-" * 30)

    service = AniListService()

    try:
        async with service:
            # Get One Piece by its AniList ID
            anime_id = 21  # One Piece ID
            result = await service.get_media_by_id(anime_id, MediaType.ANIME)

            if result:
                print(f"✅ Found by ID {anime_id}:")
                print(f"📺 Title: {result.title.romaji}")
                print(f"🏷️  English: {result.title.english}")
                print(f"📊 Score: {result.averageScore}")
                print(
                    f"📖 Description: {result.description[:100] if result.description else 'N/A'}..."
                )

                # Show some detailed info
                if result.genres:
                    print(f"🎭 Genres: {', '.join(result.genres[:5])}")
                if result.studios and result.studios.edges:
                    main_studio = next(
                        (
                            edge.node.name
                            for edge in result.studios.edges
                            if edge.isMain
                        ),
                        "Unknown",
                    )
                    print(f"🏢 Studio: {main_studio}")

            else:
                print(f"❌ No anime found with ID {anime_id}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


async def example_search_with_filters():
    """Example: Search with additional filters."""
    print("🔍 Example 4: Advanced Search with Filters")
    print("-" * 40)

    service = AniListService()

    try:
        async with service:
            # Search for anime with specific criteria
            result = await service.search_media(
                search="Naruto", media_type=MediaType.ANIME, page=1, per_page=5
            )

            if result and hasattr(result, "media") and result.media:
                print(f"✅ Found {len(result.media)} Naruto-related anime:")

                for i, anime in enumerate(result.media, 1):
                    print(f"  {i}. {anime.title.romaji}")
                    print(f"     Score: {anime.averageScore}/100")
                    print(
                        f"     Format: {anime.format.value if anime.format else 'Unknown'}"
                    )
                    print(
                        f"     Status: {anime.status.value if anime.status else 'Unknown'}"
                    )
                    print()

            else:
                print("❌ No results found")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


async def example_error_handling():
    """Example: Proper error handling for common issues."""
    print("🔍 Example 5: Error Handling")
    print("-" * 30)

    service = AniListService()

    # Test cases that might fail
    test_cases = [
        ("Valid anime", "One Piece"),
        ("Misspelled anime", "Won Peice"),
        ("Non-existent anime", "This Anime Does Not Exist 12345"),
        ("Empty search", ""),
    ]

    for test_name, search_term in test_cases:
        print(f"🧪 Testing: {test_name} ('{search_term}')")

        try:
            async with service:
                result = await service.search_anime(search_term)

                if result and hasattr(result, "media") and result.media:
                    anime = result.media[0]
                    print(f"✅ Success: Found '{anime.title.romaji}'")
                else:
                    print("⚠️  No results found")

        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ {error_type}: {e}")

        print()

        # Small delay to avoid rate limiting
        await asyncio.sleep(1)


async def example_data_conversion():
    """Example: Converting AniList data for API responses."""
    print("🔍 Example 6: Data Conversion for API Responses")
    print("-" * 45)

    service = AniListService()

    try:
        async with service:
            result = await service.search_anime("Attack on Titan")

            if result and hasattr(result, "media") and result.media:
                anime = result.media[0]

                # Convert to dictionary (like in your API endpoints)
                anime_dict = (
                    anime.model_dump() if hasattr(anime, "model_dump") else anime.dict()
                )

                print("✅ Raw AniList data converted to dict:")
                print(f"📋 Keys available: {len(anime_dict)} fields")

                # Show key fields that are useful for API responses
                key_fields = {
                    "id": anime_dict.get("id"),
                    "title": anime_dict.get("title", {}).get("romaji"),
                    "averageScore": anime_dict.get("averageScore"),
                    "episodes": anime_dict.get("episodes"),
                    "status": anime_dict.get("status"),
                    "genres": anime_dict.get("genres", [])[:3],  # First 3 genres
                }

                print("📊 Key fields for API response:")
                print(json.dumps(key_fields, indent=2, ensure_ascii=False))

                # Show how this would look in your MVP response format
                mvp_response = {
                    "type": "anime",
                    "anilist_data": anime_dict,  # This is what goes in your API
                    "tmdb_data": None,
                    # ... other fields
                }

                print("\n🎯 MVP Response Format Preview:")
                print(f"type: {mvp_response['type']}")
                print(f"anilist_data: Present ({len(anime_dict)} fields)")
                print(f"tmdb_data: {mvp_response['tmdb_data']}")

            else:
                print("❌ No data to convert")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


async def main():
    """Run all examples."""
    print("🚀 AniList Service Examples")
    print("=" * 50)
    print("Note: These examples respect rate limits and include proper error handling.")
    print("If you see 429 errors, wait a minute before running again.\n")

    # Run examples
    await example_single_search()
    await example_get_by_id()
    await example_data_conversion()
    await example_error_handling()

    print("⚠️  Skipping multiple searches example to avoid rate limiting")
    print("   Uncomment the line below to test multiple searches:")
    print("   # await example_multiple_searches_with_delay()")
    print("   # await example_search_with_filters()")

    print("\n✅ Examples completed!")
    print("\n💡 Tips:")
    print("   • Always use 'async with service:' context manager")
    print("   • Handle 429 errors gracefully with delays")
    print("   • Convert Media objects to dicts for API responses")
    print("   • Cache results when possible to reduce API calls")
    print(f"   • Current rate limit: 30 requests/minute")


if __name__ == "__main__":
    asyncio.run(main())
