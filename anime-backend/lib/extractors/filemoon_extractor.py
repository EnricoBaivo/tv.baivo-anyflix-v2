"""Filemoon extractor."""

import re
from typing import Dict, List, Optional

from ..models.base import VideoSource
from ..utils.client import HTTPClient
from .jwplayer_extractor import jwplayer_extractor
from .ytdlp_extractor import ytdlp_extractor


async def filemoon_extractor(
    url: str, headers: Optional[Dict[str, str]] = None
) -> List[VideoSource]:
    """
    Extract video sources from Filemoon.
    Based on the JavaScript filemoonExtractor function.
    Working last time: 06-09-2025
    """
    ytflp_sources = ytdlp_extractor(url)
    if ytflp_sources:
        return ytflp_sources
    client = HTTPClient()
    print(f"Fetching initial page: {url}")
    # Set default headers
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    # Merge with provided headers, removing conflicting user-agent
    if headers:
        headers = dict(headers)
        headers.pop("user-agent", None)  # Remove lowercase version
        headers.update(default_headers)
    else:
        headers = default_headers

    try:
        headers["Referer"] = url
        # Fetch the initial page
        response = await client.get(url, headers=headers)
        print(f"Initial page fetched successfully: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to fetch initial page: {response.status_code}")
            return []
        print(f"Initial page fetched successfully: {response.status_code}")
        # Look for iframe source
        iframe_match = re.search(r'iframe src="(.*?)"', response.body)

        if iframe_match:
            print(f"Found iframe URL: {iframe_match.group(1)}")
            iframe_url = iframe_match.group(1)

            # Fetch the iframe content
            iframe_headers = {
                "Referer": url,
                "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
                "User-Agent": headers["User-Agent"],
            }

            iframe_response = await client.get(iframe_url, headers=iframe_headers)

            if iframe_response.status_code == 200:
                response = iframe_response
                headers = iframe_headers
            else:
                print(f"Failed to fetch iframe content: {iframe_response.status_code}")

        # Extract video sources using JWPlayer extractor
        return await jwplayer_extractor(response.body, headers)

    except Exception as e:
        print(f"Failed to extract video sources: {e}")
        return []
