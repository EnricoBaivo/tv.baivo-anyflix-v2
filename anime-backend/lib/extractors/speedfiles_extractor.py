"""SpeedFiles extractor."""

import re
from typing import Dict, List, Optional

from ..models.base import VideoSource
from ..utils.base64_utils import Base64Utils
from ..utils.client import HTTPClient
from ..utils.string_utils import StringUtils
from .ytdlp_extractor import ytdlp_extractor


async def speedfiles_extractor(
    url: str, headers: Optional[Dict[str, str]] = None
) -> List[VideoSource]:
    """
    Extract video sources from SpeedFiles.
    Based on the JavaScript speedfilesExtractor function.
    """
    ytflp_sources = ytdlp_extractor(url)
    if ytflp_sources:
        return ytflp_sources
    client = HTTPClient()

    try:
        # Fetch the page content
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return []

        # Find script with variable declarations
        script_match = re.search(
            r"<script[^>]*>.*?var\s+[^<]*</script>", response.body, re.DOTALL
        )
        if not script_match:
            return []

        script_content = script_match.group(0)

        # Extract base64 encoded string
        # Look for variables with base64-like content (containing g-z or G-Z)
        b64 = None
        for match in re.finditer(
            r'(?:var|let|const)\s*\w+\s*=\s*["\']([^"\']+)["\']', script_content
        ):
            candidate = match.group(1)
            if re.search(r"[g-zG-Z]", candidate):
                b64 = candidate
                break

        if not b64:
            return []

        # Multi-step decoding process as in the JavaScript version

        # Step 1: decode b64 => b64
        step1_bytes = Base64Utils.decode(b64)
        step1_reversed = Base64Utils.reverse_bytes(step1_bytes)
        step1_decoded = Base64Utils.decode_utf8(step1_reversed)
        step1_swapped = StringUtils.swapcase(step1_decoded)

        # Step 2: decode b64 => hex
        step2_bytes = Base64Utils.decode(step1_swapped)
        step2_reversed = Base64Utils.reverse_bytes(step2_bytes)
        step2_hex = Base64Utils.decode_utf8(step2_reversed)

        # Step 3: decode hex => b64
        step3_chars = []
        for i in range(0, len(step2_hex), 2):
            if i + 1 < len(step2_hex):
                hex_pair = step2_hex[i : i + 2]
                try:
                    char_code = int(hex_pair, 16) - 3
                    step3_chars.append(char_code)
                except ValueError:
                    continue

        step3_chars.reverse()
        step3_string = "".join(chr(c) for c in step3_chars if 0 <= c <= 127)
        step3_swapped = StringUtils.swapcase(step3_string)

        # Step 4: decode b64 => final URL
        final_bytes = Base64Utils.decode(step3_swapped)
        video_url = Base64Utils.decode_utf8(final_bytes)

        if not video_url or not video_url.startswith("http"):
            return []

        return [
            VideoSource(url=video_url, original_url=video_url, quality="", headers=None)
        ]

    except Exception:
        return []
