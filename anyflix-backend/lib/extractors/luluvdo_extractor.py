"""Luluvdo extractor."""

import re
from typing import Dict, List, Optional

from ..models.base import VideoSource
from ..utils.client import HTTPClient
from .jwplayer_extractor import jwplayer_extractor
from .ytdlp_extractor import ytdlp_extractor


async def luluvdo_extractor(
    url: str, headers: Optional[Dict[str, str]] = None
) -> List[VideoSource]:
    """
    Extract video sources from Luluvdo.
    Based on the JavaScript luluvdoExtractor function.
    """
    ytflp_sources = ytdlp_extractor(url)
    if ytflp_sources:
        return ytflp_sources
    client = HTTPClient()

    try:
        # Parse URL to extract base and file code
        url_match = re.match(r"(.*?://.*?)\/.*\/(.*)", url)
        if not url_match:
            return []

        base_url = url_match.group(1)
        file_code = url_match.group(2)

        # Construct embed URL
        embed_url = f"{base_url}/dl?op=embed&file_code={file_code}"

        # Set headers
        request_headers = {"user-agent": "Mangayomi"}

        # Merge with provided headers
        if headers:
            request_headers.update(headers)

        # Fetch embed page
        response = await client.get(embed_url, headers=request_headers)

        if response.status_code != 200:
            return []

        # Extract video sources using JWPlayer extractor
        return await jwplayer_extractor(response.body, request_headers)

    except Exception:
        return []
