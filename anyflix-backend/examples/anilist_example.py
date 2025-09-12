#!/usr/bin/env python3
"""Example usage of AniListService."""

import asyncio
import json
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.models.anilist import Media, MediaType
from lib.services.anilist_service import AniListService


async def demonstrate_anilist_service():
    """Demonstrate AniListService functionality."""
    print("🎬 AniList API Service Demo")
    print("=" * 50)

    async with AniListService() as anilist:

        # 1. Get media by ID
        print("\n1. Getting anime by ID (Cowboy Bebop - ID: 1)")
        try:
            media = await anilist.get_media_by_id(1)
            if media:
                print(f"   Title: {media.title.userPreferred}")
                print(f"   Type: {media.type}")
                print(f"   Episodes: {media.episodes}")
                print(f"   Score: {media.averageScore}")
                print(f"   Genres: {', '.join(media.genres or [])}")
            else:
                print("   Media not found")
        except Exception as e:
            print(f"   Error: {e}")

        # 2. Search for anime
        print("\n2. Searching for anime: 'Attack on Titan'")
        try:
            results = await anilist.search_anime("Attack on Titan", per_page=3)
            if results and results.media:
                for i, anime in enumerate(results.media, 1):
                    print(f"   {i}. {anime.title.userPreferred} (ID: {anime.id})")
                    print(
                        f"      Score: {anime.averageScore}, Episodes: {anime.episodes}"
                    )
        except Exception as e:
            print(f"   Error: {e}")

        # 3. Get trending anime
        print("\n3. Getting trending anime (top 5)")
        try:
            trending = await anilist.get_trending_anime(per_page=5)
            if trending and trending.media:
                for i, anime in enumerate(trending.media, 1):
                    print(f"   {i}. {anime.title.userPreferred}")
                    print(
                        f"      Score: {anime.averageScore}, Popularity: {anime.popularity}"
                    )
        except Exception as e:
            print(f"   Error: {e}")

        # 4. Get popular anime
        print("\n4. Getting popular anime (top 5)")
        try:
            popular = await anilist.get_popular_anime(per_page=5)
            if popular and popular.media:
                for i, anime in enumerate(popular.media, 1):
                    print(f"   {i}. {anime.title.userPreferred}")
                    print(
                        f"      Score: {anime.averageScore}, Popularity: {anime.popularity}"
                    )
        except Exception as e:
            print(f"   Error: {e}")

        # 5. Get seasonal anime
        print("\n5. Getting Fall 2023 anime (top 5)")
        try:
            seasonal = await anilist.get_seasonal_anime("FALL", 2023, per_page=5)
            if seasonal and seasonal.media:
                for i, anime in enumerate(seasonal.media, 1):
                    print(f"   {i}. {anime.title.userPreferred}")
                    if anime.startDate:
                        print(
                            f"      Started: {anime.startDate.year}-{anime.startDate.month or '??'}"
                        )
        except Exception as e:
            print(f"   Error: {e}")

        # 6. Get upcoming anime
        print("\n6. Getting upcoming anime (top 3)")
        try:
            upcoming = await anilist.get_upcoming_anime(per_page=3)
            if upcoming and upcoming.media:
                for i, anime in enumerate(upcoming.media, 1):
                    print(f"   {i}. {anime.title.userPreferred}")
                    print(f"      Status: {anime.status}")
                    if anime.startDate:
                        start_year = anime.startDate.year or "TBA"
                        print(f"      Expected: {start_year}")
        except Exception as e:
            print(f"   Error: {e}")

        # 7. Get detailed media information with relations
        print("\n7. Getting detailed info for Attack on Titan (ID: 16498)")
        try:
            detailed = await anilist.get_media_by_id(16498, detailed=True)
            if detailed:
                print(f"   Title: {detailed.title.userPreferred}")
                print(
                    f"   Description: {detailed.description[:100] if detailed.description else 'N/A'}..."
                )

                # Show relations if available
                if detailed.relations and detailed.relations.edges:
                    print(f"   Relations ({len(detailed.relations.edges)}):")
                    for edge in detailed.relations.edges[:3]:  # Show first 3
                        if edge.node and edge.node.title:
                            relation_type = edge.relationType or "UNKNOWN"
                            print(
                                f"      - {relation_type}: {edge.node.title.userPreferred}"
                            )

                # Show studios if available
                if detailed.studios and detailed.studios.edges:
                    print("   Studios:")
                    for edge in detailed.studios.edges:
                        if edge.node:
                            main_indicator = " (Main)" if edge.isMain else ""
                            print(f"      - {edge.node.name}{main_indicator}")

                # Show external links if available
                if detailed.externalLinks:
                    print(f"   External Links ({len(detailed.externalLinks)}):")
                    for link in detailed.externalLinks[:3]:  # Show first 3
                        print(f"      - {link.site}: {link.url}")

        except Exception as e:
            print(f"   Error: {e}")

        # 8. Search manga
        print("\n8. Searching for manga: 'One Piece'")
        try:
            manga_results = await anilist.search_manga("One Piece", per_page=3)
            if manga_results and manga_results.media:
                for i, manga in enumerate(manga_results.media, 1):
                    print(f"   {i}. {manga.title.userPreferred} (ID: {manga.id})")
                    chapters = manga.chapters or "Ongoing"
                    print(f"      Chapters: {chapters}, Score: {manga.averageScore}")
        except Exception as e:
            print(f"   Error: {e}")


async def search_and_display_detailed(
    query: str, media_type: MediaType = MediaType.ANIME
):
    """Search for media and display detailed information."""
    print(f"\n🔍 Searching for {media_type.value.lower()}: '{query}'")
    print("-" * 40)

    async with AniListService() as anilist:
        try:
            results = await anilist.search_media(query, media_type, per_page=1)

            if not results or not results.media:
                print("No results found.")
                return

            # Get the first result and fetch detailed information
            first_result = results.media[0]
            detailed = await anilist.get_media_by_id(first_result.id, detailed=True)

            if not detailed:
                print("Could not fetch detailed information.")
                return

            # Display detailed information
            print(f"Title: {detailed.title.userPreferred}")
            if (
                detailed.title.english
                and detailed.title.english != detailed.title.userPreferred
            ):
                print(f"English: {detailed.title.english}")
            if detailed.title.native:
                print(f"Native: {detailed.title.native}")

            print(f"Type: {detailed.type} - {detailed.format}")
            print(f"Status: {detailed.status}")

            if detailed.episodes:
                print(f"Episodes: {detailed.episodes}")
            if detailed.chapters:
                print(f"Chapters: {detailed.chapters}")
            if detailed.duration:
                print(f"Duration: {detailed.duration} minutes")

            if detailed.startDate:
                start_date = f"{detailed.startDate.year or '????'}"
                if detailed.startDate.month:
                    start_date += f"-{detailed.startDate.month:02d}"
                if detailed.startDate.day:
                    start_date += f"-{detailed.startDate.day:02d}"
                print(f"Start Date: {start_date}")

            if detailed.season and detailed.seasonYear:
                print(f"Season: {detailed.season} {detailed.seasonYear}")

            if detailed.averageScore:
                print(f"Average Score: {detailed.averageScore}/100")

            if detailed.popularity:
                print(f"Popularity: #{detailed.popularity}")

            if detailed.genres:
                print(f"Genres: {', '.join(detailed.genres)}")

            if detailed.description:
                # Clean up description (remove HTML tags)
                import re

                clean_desc = re.sub(r"<[^>]+>", "", detailed.description)
                print(f"Description: {clean_desc[:200]}...")

            if detailed.coverImage and detailed.coverImage.large:
                print(f"Cover Image: {detailed.coverImage.large}")

            if detailed.trailer:
                print(f"Trailer: {detailed.trailer.site}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("Starting AniList API demonstration...")

    # Run the main demonstration
    asyncio.run(demonstrate_anilist_service())

    # Additional detailed searches
    asyncio.run(search_and_display_detailed("Demon Slayer"))
    asyncio.run(search_and_display_detailed("Naruto", MediaType.ANIME))

    print("\n✅ Demo completed!")
