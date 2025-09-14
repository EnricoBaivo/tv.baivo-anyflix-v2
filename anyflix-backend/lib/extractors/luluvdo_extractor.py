"""Luluvdo extractor."""

import re

from lib.extractors.jwplayer_extractor import jwplayer_extractor
from lib.extractors.ytdlp_extractor import ytdlp_extractor
from lib.models.base import VideoSource
from lib.utils.caching import ServiceCacheConfig, cached
from lib.utils.client import HTTPClient


@cached(ttl=ServiceCacheConfig.EXTRACTOR_TTL, key_prefix="luluvdo_extract")
async def luluvdo_extractor(
    url: str, headers: dict[str, str] | None = None
) -> list[VideoSource]:
    """
    Extract video sources from Luluvdo.
    Based on the JavaScript luluvdoExtractor function.
    """
    ytflp_sources = await ytdlp_extractor(url)
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
        return await jwplayer_extractor(response.body, request_headers, host="luluvdo")

    except Exception:
        return []
