#!/usr/bin/env python3
"""
API Integration Example

Shows how to integrate AniList service into your API endpoints,
similar to how it's used in app/routers/sources.py

Usage: python examples/api_integration_example.py (from project root)
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, Optional

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.services.anilist_service import AniListService
from lib.services.tmdb_service import TMDBService

# Setup logging like in your app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def enrich_anime_with_metadata(anime_name: str) -> Dict[str, Any]:
    """
    Example function that enriches anime data with AniList metadata.
    This mirrors the logic in your sources.py file.
    """
    print(f"🔍 Enriching '{anime_name}' with metadata...")

    # Initialize services (like in your sources.py)
    anilist_service = AniListService()

    # Base response structure
    result = {
        "name": anime_name,
        "type": "anime",
        "anilist_data": None,
        "tmdb_data": None,
        "match_confidence": None,
    }

    # Try to get AniList data (like in your enrich_with_metadata function)
    try:
        async with anilist_service:
            anilist_data = await anilist_service.search_anime(anime_name)

            if anilist_data and hasattr(anilist_data, "media") and anilist_data.media:
                # Take the first result and convert to dict (like in your fixed code)
                first_result = anilist_data.media[0]
                result["anilist_data"] = (
                    first_result.model_dump()
                    if hasattr(first_result, "model_dump")
                    else first_result.dict()
                )
                result["match_confidence"] = 1.0
                print(f"✅ Found AniList data for '{anime_name}'")
            else:
                result["anilist_data"] = None
                print(f"⚠️  No AniList data found for '{anime_name}'")

    except Exception as e:
        logger.warning(f"Failed to enrich with AniList data: {e}")
        result["anilist_data"] = None

        # Check if it's a rate limit error
        if "429" in str(e) or "Too Many Requests" in str(e):
            print(f"⏳ Rate limited for '{anime_name}' - this is expected")

    return result


async def simulate_series_detail_endpoint(
    anime_url: str, anime_name: str
) -> Dict[str, Any]:
    """
    Simulates your get_series_detail endpoint logic for metadata enrichment.
    """
    print(f"🎬 Simulating series detail for: {anime_name}")

    anilist_service = AniListService()

    # Base response (like in your get_series_detail function)
    response_data = {
        "type": "anime",
        "series": {
            "slug": anime_url.split("/")[-1] if "/" in anime_url else "unknown",
            "seasons": [],  # Would be populated by provider data
            "movies": [],  # Would be populated by provider data
        },
        "tmdb_data": None,
        "anilist_data": None,
    }

    # Add AniList metadata (like in your sources.py lines 285-295)
    try:
        async with anilist_service:
            anilist_data = await anilist_service.search_anime(anime_name)

            if anilist_data and hasattr(anilist_data, "media") and anilist_data.media:
                # Take the first result and convert to dict
                first_result = anilist_data.media[0]
                response_data["anilist_data"] = (
                    first_result.model_dump()
                    if hasattr(first_result, "model_dump")
                    else first_result.dict()
                )
                print(f"✅ Added AniList metadata to series detail")
            else:
                print(f"⚠️  No AniList match found")

    except Exception as e:
        logger.warning(f"Failed to get AniList data for series: {e}")
        if "429" in str(e):
            print("⏳ Rate limited - metadata will be null (expected behavior)")

    return response_data


async def demonstrate_rate_limiting():
    """
    Shows what happens when you hit rate limits and how to handle it.
    """
    print("🚦 Demonstrating Rate Limiting Behavior")
    print("-" * 40)

    anime_list = [
        "One Piece",
        "Naruto",
        "Attack on Titan",
        "Demon Slayer",
        "My Hero Academia",
    ]

    successful_enrichments = 0
    rate_limited_count = 0

    for anime in anime_list:
        result = await enrich_anime_with_metadata(anime)

        if result["anilist_data"] is not None:
            successful_enrichments += 1
        else:
            rate_limited_count += 1

        # Small delay between requests
        await asyncio.sleep(1)

    print(f"\n📊 Results:")
    print(f"✅ Successful enrichments: {successful_enrichments}")
    print(f"⏳ Rate limited/failed: {rate_limited_count}")
    print(f"📈 Success rate: {successful_enrichments/len(anime_list)*100:.1f}%")

    if rate_limited_count > 0:
        print("\n💡 This is normal behavior when hitting rate limits.")
        print("   Your API gracefully handles this by returning null for metadata.")


async def show_data_structure():
    """
    Shows the actual data structure you get from AniList.
    """
    print("📋 AniList Data Structure Example")
    print("-" * 35)

    service = AniListService()

    try:
        async with service:
            result = await service.search_anime("Attack on Titan")

            if result and hasattr(result, "media") and result.media:
                anime = result.media[0]
                anime_dict = (
                    anime.model_dump() if hasattr(anime, "model_dump") else anime.dict()
                )

                print("✅ Sample AniList data structure:")
                print(f"📊 Total fields: {len(anime_dict)}")

                # Show key fields that are useful
                key_info = {
                    "id": anime_dict.get("id"),
                    "title": {
                        "romaji": anime_dict.get("title", {}).get("romaji"),
                        "english": anime_dict.get("title", {}).get("english"),
                    },
                    "averageScore": anime_dict.get("averageScore"),
                    "episodes": anime_dict.get("episodes"),
                    "status": anime_dict.get("status"),
                    "genres": anime_dict.get("genres", [])[:3],
                    "description": (
                        anime_dict.get("description", "")[:100] + "..."
                        if anime_dict.get("description")
                        else None
                    ),
                }

                print("\n🔑 Key fields available:")
                for key, value in key_info.items():
                    print(f"  {key}: {value}")

                print(f"\n📋 All available fields:")
                fields = list(anime_dict.keys())
                for i in range(0, len(fields), 5):
                    print(f"  {', '.join(fields[i:i+5])}")

            else:
                print("❌ No data available to show structure")

    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all API integration examples."""
    print("🚀 AniList API Integration Examples")
    print("=" * 50)
    print("These examples show how AniList service integrates with your API.\n")

    # Show data structure first
    await show_data_structure()
    print("\n" + "=" * 50 + "\n")

    # Show single enrichment
    result = await enrich_anime_with_metadata("One Piece")
    print(
        f"📝 Result: {result['name']} - AniList data: {'✅ Present' if result['anilist_data'] else '❌ Null'}"
    )
    print("\n" + "=" * 50 + "\n")

    # Show series detail simulation
    series_result = await simulate_series_detail_endpoint(
        "/anime/stream/attack-on-titan", "Attack on Titan"
    )
    print(
        f"📺 Series detail result: AniList data {'✅ Present' if series_result['anilist_data'] else '❌ Null'}"
    )
    print("\n" + "=" * 50 + "\n")

    # Demonstrate rate limiting (commented out to avoid hitting limits)
    print("⚠️  Rate limiting demo disabled to preserve API quota.")
    print("   Uncomment the line below to test rate limiting behavior:")
    print("   # await demonstrate_rate_limiting()")

    print("\n✅ API integration examples completed!")
    print("\n💡 Key takeaways:")
    print("   • AniList data is converted to dict for API responses")
    print("   • Rate limiting is handled gracefully with null fallbacks")
    print("   • Always use async context managers")
    print("   • First search result is used for metadata enrichment")


if __name__ == "__main__":
    asyncio.run(main())
