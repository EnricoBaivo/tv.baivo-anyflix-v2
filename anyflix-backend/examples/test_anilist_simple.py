#!/usr/bin/env python3
"""
Simple AniList Service Test

A minimal example to test if the AniList service is working.
Run this to verify your setup before using the full examples.

Usage: python examples/test_anilist_simple.py (from project root)
"""

import asyncio
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.services.anilist_service import AniListService


async def quick_test():
    """Quick test to verify AniList service is working."""
    print("🧪 Quick AniList Service Test")
    print("-" * 30)

    service = AniListService()

    try:
        async with service:
            print("📡 Testing connection to AniList API...")

            # Simple search for a well-known anime
            result = await service.search_anime("One Piece")

            if result and hasattr(result, "media") and result.media:
                anime = result.media[0]
                print("✅ AniList service is working!")
                print(f"📺 Found: {anime.title.romaji}")
                print(f"📊 Score: {anime.averageScore}/100")

                # Test data conversion (like in your API)
                anime_dict = (
                    anime.model_dump() if hasattr(anime, "model_dump") else anime.dict()
                )
                print(f"📋 Data conversion: {len(anime_dict)} fields available")

                return True
            else:
                print("❌ No results returned")
                return False

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Too Many Requests" in error_msg:
            print("⏳ Rate limited - API is working but needs to wait")
            print("   Try again in 1-2 minutes")
            return True  # Service is working, just rate limited
        else:
            print(f"❌ Error: {e}")
            return False


async def main():
    success = await quick_test()

    if success:
        print("\n🎉 Success! AniList service is ready to use.")
        print(
            "   Run 'python examples/anilist_service_example.py' for detailed examples."
        )
    else:
        print("\n💥 Service test failed. Check your connection and try again.")


if __name__ == "__main__":
    asyncio.run(main())
