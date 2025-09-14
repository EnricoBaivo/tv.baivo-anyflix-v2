"""Vidoza extractor."""

import re

from lib.extractors.ytdlp_extractor import ytdlp_extractor
from lib.models.base import VideoSource
from lib.utils.caching import ServiceCacheConfig, cached
from lib.utils.client import HTTPClient


@cached(ttl=ServiceCacheConfig.EXTRACTOR_TTL, key_prefix="vidoza_extract")
async def vidoza_extractor(
    url: str, headers: dict[str, str] | None = None
) -> list[VideoSource]:
    """
    Extract video sources from Vidoza.
    Based on the JavaScript vidozaExtractor function.
    """
    client = HTTPClient(follow_redirects=True)
    ytflp_sources = await ytdlp_extractor(url)
    if ytflp_sources:
        return ytflp_sources
    try:
        # Fetch the page content with redirects
        response = await client.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return []

        # Extract direct MP4 video URL from the response
        mp4_match = re.search(r"https://[^\s]*\.mp4", response.body)
        if not mp4_match:
            print("Failed to find MP4 URL")
            return []
        print(f"Found MP4 URL: {mp4_match.group(0)}")
        video_url = mp4_match.group(0)

        return [
            VideoSource(
                url=video_url, original_url=video_url, quality="", headers=headers
            )
        ]

    except Exception as e:
        print(f"Failed to extract video sources: {e}")
        return []
