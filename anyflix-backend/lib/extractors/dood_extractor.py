"""Doodstream extractor."""

import re
import time
from typing import Dict, List, Optional

from ..models.base import VideoSource
from ..utils.caching import ServiceCacheConfig, cached
from ..utils.client import HTTPClient
from ..utils.helpers import get_random_string
from .ytdlp_extractor import ytdlp_extractor


@cached(ttl=ServiceCacheConfig.EXTRACTOR_TTL, key_prefix="dood_extract")
async def dood_extractor(
    url: str, headers: Optional[Dict[str, str]] = None
) -> List[VideoSource]:
    """
    Extract video sources from Doodstream.
    Based on the JavaScript doodExtractor function.
    """
    ytflp_sources = await ytdlp_extractor(url)
    if ytflp_sources:
        return ytflp_sources
    client = HTTPClient()

    try:
        # Follow redirects manually to get final URL
        response = await client.get(url, follow_redirects=False)

        while (
            response.status_code in [301, 302, 303, 307, 308]
            and "location" in response.headers
        ):
            redirect_url = response.headers["location"]
            response = await client.get(redirect_url, follow_redirects=False)

        final_url = response.url if hasattr(response, "url") else url
        final_response = response

        # If we got a redirect response, fetch the final URL content
        if response.status_code in [301, 302, 303, 307, 308]:
            final_url = response.headers.get("location", url)
            final_response = await client.get(final_url)

        # Extract dood host from final URL
        host_match = re.search(r"https://([^/]+)/", final_url)
        if not host_match:
            return []

        dood_host = host_match.group(1)

        # Extract MD5 path from response body
        md5_match = re.search(r"'/pass_md5/([^']+)'", final_response.body)
        if not md5_match:
            return []

        md5_path = md5_match.group(1)
        token = md5_path.split("/")[-1]

        # Generate expiry timestamp and random string
        expiry = str(int(time.time() * 1000))
        random_string = get_random_string(10)

        # Get the video URL base
        md5_url = f"https://{dood_host}/pass_md5/{md5_path}"
        md5_response = await client.get(md5_url, headers={"Referer": final_url})

        if md5_response.status_code != 200:
            return []

        # Construct final video URL
        video_url = f"{md5_response.body}{random_string}?token={token}&expiry={expiry}"

        # Set appropriate headers
        video_headers = {"User-Agent": "Mangayomi", "Referer": dood_host}

        return [
            VideoSource(
                url=video_url,
                original_url=video_url,
                quality="",
                host="doodstream",
                requires_proxy=False,  # DoodStream doesn't need proxy
                headers=video_headers,
            )
        ]

    except Exception:
        return []
