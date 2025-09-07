"""Vidmoly extractor."""

import logging
import re
from typing import Dict, List, Optional

from ..models.base import VideoSource
from ..utils.client import HTTPClient
from .m3u8_extractor import m3u8_extractor
from .ytdlp_extractor import ytdlp_extractor


async def vidmoly_extractor(
    url: str, headers: Optional[Dict[str, str]] = None
) -> List[VideoSource]:
    """
    Extract video sources from Vidmoly.
    Based on the JavaScript vidmolyExtractor function.
    Working last time: 06-09-2025
    """
    ytflp_sources = ytdlp_extractor(url)
    if ytflp_sources:
        # Update ytdlp sources to mark them as vidmoly and requiring proxy
        for source in ytflp_sources:
            source.host = "vidmoly"
            source.requires_proxy = True
        return ytflp_sources
    client = HTTPClient(follow_redirects=True)

    try:
        # Fetch the page content with redirects
        response = await client.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return []
        # Extract M3U8 playlist URL from the response
        m3u8_match = re.search(r"https://[^\s]*\.m3u8[^\s]*", response.body)
        print(f"M3U8 match: {m3u8_match}")
        if not m3u8_match:
            print(f"Failed to find M3U8 playlist URL")
            return []
        print(f"Found M3U8 playlist URL: {m3u8_match.group(0)}")
        playlist_url = m3u8_match.group(0)

        # Extract video sources from M3U8 playlist
        m3u8_headers = {"Referer": "https://vidmoly.to", "Origin": "https://vidmoly.to"}

        # Merge with provided headers if any
        if headers:
            m3u8_headers.update(headers)

        # Get video sources from M3U8 extractor
        video_sources = await m3u8_extractor(playlist_url, m3u8_headers)

        # Update each source to mark it as vidmoly and requiring proxy
        for source in video_sources:
            source.host = "vidmoly"
            source.requires_proxy = True

        return video_sources

    except Exception as e:
        logging.error(f"Failed to extract video sources: {e}")
        return []
