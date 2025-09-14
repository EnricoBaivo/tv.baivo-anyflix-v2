"""VOE video extractor."""

# coding=utf-8
import base64
import json
import logging
import os
import random
import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from lib.models.base import VideoSource
from lib.utils.caching import ServiceCacheConfig, cached

logger = logging.getLogger(__name__)


@cached(ttl=ServiceCacheConfig.EXTRACTOR_TTL, key_prefix="voe_extract")
async def voe_extractor(
    url: str, _headers: dict[str, str] | None = None
) -> list[VideoSource]:
    """
    Extract video sources from VOE (voe.sx) links.
    source: https://github.com/p4ul17/voe-dl

    Args:
        url: The VOE URL to extract from
        headers: Optional HTTP headers

    Returns:
        List of VideoSource objects
    """
    import asyncio

    # Run the synchronous extract_voe function in a thread pool
    result = await asyncio.to_thread(extract_voe, url)

    # extract_voe now returns List[VideoSource] or empty list
    if isinstance(result, list):
        return result
    # Fallback for unexpected return types
    return []


# List of common user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Create a session that persists across requests
session = requests.Session()


def get_browser_headers(url=None):
    """Generate realistic browser headers with optional referer based on URL"""
    parsed_url = urlparse(url) if url else None
    referer = f"{parsed_url.scheme}://{parsed_url.netloc}/" if parsed_url else ""

    headers = {
        "User-Agent": random.choice(USER_AGENTS),  # noqa: S311 - Non-cryptographic use
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none" if not referer else "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "DNT": "1",
        "Priority": "u=1",
    }

    if referer:
        headers["Referer"] = referer

    return headers


# Method-8 dedicated helpers (obfuscated JSON inside <script type="application/json">) | @Domkeykong
def _rot13(text: str) -> str:
    """Apply ROT13 cipher (letters only)."""
    out = []
    for ch in text:
        o = ord(ch)
        if 65 <= o <= 90:
            out.append(chr(((o - 65 + 13) % 26) + 65))
        elif 97 <= o <= 122:
            out.append(chr(((o - 97 + 13) % 26) + 97))
        else:
            out.append(ch)
    return "".join(out)


def _replace_patterns(txt: str) -> str:
    """Strip marker substrings used as obfuscation separators."""
    for pat in ["@$", "^^", "~@", "%?", "*~", "!!", "#&"]:
        txt = txt.replace(pat, "")
    return txt


def _shift_chars(text: str, shift: int) -> str:
    """Shift character code-points by *-shift* (decode)."""
    return "".join(chr(ord(c) - shift) for c in text)


def _safe_b64_decode(s: str) -> str:
    """Base64 decode with safe padding and utf-8 fallback."""
    pad = len(s) % 4
    if pad:
        s += "=" * (4 - pad)
    return base64.b64decode(s).decode("utf-8", errors="replace")


def deobfuscate_embedded_json(raw_json: str) -> dict | str | None:
    """Return a dict or str extracted from the obfuscated JSON array found in <script type="application/json">."""
    try:
        arr = json.loads(raw_json)
        if not (isinstance(arr, list) and arr and isinstance(arr[0], str)):
            return None
        obf = arr[0]
    except json.JSONDecodeError:
        return None

    try:
        step1 = _rot13(obf)
        step2 = _replace_patterns(step1)
        step3 = _safe_b64_decode(step2)
        step4 = _shift_chars(step3, 3)
        step5 = step4[::-1]
        step6 = _safe_b64_decode(step5)
        try:
            return json.loads(step6)  # ideally a dict with direct_access_url / source
        except json.JSONDecodeError:
            return step6  # return plain string for fallback regex search
    except (ValueError, KeyError, TypeError):
        return None


def extract_voe(URL, lang=None, type_str=None):
    URL = str(URL)

    # Add a small random delay to mimic human behavior
    time.sleep(random.uniform(1, 3))  # noqa: S311 - Non-cryptographic use

    # Get browser-like headers
    headers = get_browser_headers(URL)
    video_source_list = []
    try:
        # Use the session for persistent cookies
        html_page = session.get(URL, headers=headers, timeout=30)
        html_page.raise_for_status()  # Raise exception for 4XX/5XX responses

        # Handle cloudflare or other protection
        if html_page.status_code == 403 or "captcha" in html_page.text.lower():
            logger.warning(
                "Access denied or captcha detected for %s. Trying with different headers...",
                URL,
            )
            # Try again with different headers after a delay
            time.sleep(random.uniform(3, 5))  # noqa: S311 - Non-cryptographic use
            headers = get_browser_headers(URL)
            headers["User-Agent"] = random.choice(USER_AGENTS)  # noqa: S311 - Non-cryptographic use
            html_page = session.get(URL, headers=headers, timeout=30)
            html_page.raise_for_status()

        soup = BeautifulSoup(html_page.content, "html.parser")

        # logger.debug("HTML page content: %s", html_page.text)

        redirect_patterns = [
            "window.location.href = '",
            "window.location = '",
            "location.href = '",
            "window.location.replace('",
            "window.location.assign('",
            'window.location="',
            'window.location.href="',
        ]

        # Check for redirects in any script tag
        script_tags = soup.find_all("script")
        for script in script_tags:
            if script.string:
                for pattern in redirect_patterns:
                    if pattern in script.string:
                        L = len(pattern)
                        i0 = script.string.find(pattern)
                        closing_quote = "'" if pattern.endswith("'") else '"'
                        i1 = script.string.find(closing_quote, i0 + L)
                        if i1 > i0:
                            url = script.string[i0 + L : i1]
                            logger.info("Detected redirect to: %s", url)
                            return extract_voe(url)

        # Try multiple methods to find the title
        name = None
        for meta_tag in ["og:title", "twitter:title", "title"]:
            name_find = soup.find("meta", attrs={"property": meta_tag}) or soup.find(
                "meta", attrs={"name": meta_tag}
            )
            if name_find and name_find.get("content"):
                name = name_find["content"]
                break

        # If meta tags fail, try the title tag
        if not name and soup.title and soup.title.string:
            name = soup.title.string
        # Solo.Leveling.S01E01.German.720p.AAC.WebRip.x264-GSD.mp4
        if name:
            # Clean the filename to avoid issues
            name = re.sub(r'[\\/*?:"<>|]', "_", name)
            name = name.replace(" ", "_")
            logger.info("Name of file: %s", name)
            # Extract quality from filename (720p, 1080p, 480p, etc.)
            quality_match = re.search(r"\b(\d{3,4}p)\b", name, re.IGNORECASE)
            quality = quality_match.group(1).lower() if quality_match else "unknown"
        else:
            logger.warning("Could not find the name of the file. Using default name.")
            name = URL.split("/")[
                -1
            ]  # Use the last part of the URL as the default file name
            if not name or name == "":
                name = f"extract_voe_{int(time.time())}"
            logger.info("Using default file name: %s", name)

        # Enhanced source detection - multiple patterns and approaches
        source_json = None

        # Method 1: Look for "var sources" pattern
        sources_find = soup.find_all(string=re.compile("var sources"))
        if sources_find:
            sources_find = str(sources_find)
            try:
                slice_start = sources_find.index("var sources")
                source = sources_find[slice_start:]
                slice_end = source.index(";")
                source = source[:slice_end]
                source = source.replace("var sources = ", "")
                source = source.replace("'", '"')
                source = source.replace("\\n", "")
                source = source.replace("\\", "")

                # Check for "Bait" sources
                if is_bait_source(source):
                    logger.debug("Ignoring bait source: %s", source)
                    source_json = None
                else:
                    # Clean up JSON for parsing
                    strToReplace = ","
                    replacementStr = ""
                    source = replacementStr.join(source.rsplit(strToReplace, 1))
                    source_json = json.loads(source)
                    logger.info("Found sources using var sources pattern")
            except (ValueError, json.JSONDecodeError):
                logger.exception("Error parsing sources")
                source_json = None

        # Method 2: Look for script tags with sources
        if not source_json:
            scripts = soup.find_all("script")
            for script in scripts:
                if not script.string:
                    continue

                # Look for different patterns
                patterns = [
                    "var sources",
                    "sources =",
                    "sources:",
                    '"sources":',
                    "'sources':",
                ]

                for pattern in patterns:
                    if pattern in script.string:
                        try:
                            # Extract JSON-like structure
                            script_text = script.string

                            # Find the start of the sources object
                            start_idx = script_text.find(pattern)
                            if start_idx == -1:
                                continue

                            # Find the opening brace
                            brace_idx = script_text.find("{", start_idx)
                            if brace_idx == -1:
                                continue

                            # Count braces to find the matching closing brace
                            brace_count = 1
                            end_idx = brace_idx + 1

                            while brace_count > 0 and end_idx < len(script_text):
                                if script_text[end_idx] == "{":
                                    brace_count += 1
                                elif script_text[end_idx] == "}":
                                    brace_count -= 1
                                end_idx += 1

                            if brace_count == 0:
                                json_str = script_text[brace_idx:end_idx]
                                # Clean up the JSON string
                                json_str = json_str.replace("'", '"')

                                # Try to parse the JSON
                                try:
                                    source_json = json.loads(json_str)
                                    logger.info(
                                        "Found sources using pattern: %s", pattern
                                    )
                                    break
                                except json.JSONDecodeError:
                                    pass
                        except (ValueError, TypeError, AttributeError):
                            logger.exception("Error extracting sources from script")

                if source_json:
                    break

        # Method 3: Look for data attributes in video tags
        if not source_json:
            video_tags = soup.find_all("video")
            for video in video_tags:
                src = video.get("src")
                if src:
                    if is_bait_source(src):
                        logger.debug("Ignoring bait source: %s", src)
                        continue
                    logger.info("Found direct video source: %s", src)
                    source_json = {"mp4": src}
                    break

                # Check for source tags inside video
                source_tags = video.find_all("source")
                if source_tags:
                    for source_tag in source_tags:
                        src = source_tag.get("src")
                        if src:
                            if is_bait_source(src):
                                logger.debug("Ignoring bait source: %s", src)
                                continue
                            type_attr = source_tag.get("type", "")
                            if "mp4" in type_attr:
                                source_json = {"mp4": src}
                            elif "m3u8" in type_attr or "hls" in type_attr:
                                source_json = {"hls": src}
                            else:
                                source_json = {"mp4": src}  # Default to mp4
                            logger.info("Found video source from source tag: %s", src)
                            break

                if source_json:
                    break

        # Method 4: Look for m3u8 or mp4 URLs in the page
        if not source_json:
            logger.info("Searching for direct media URLs in page...")
            # Look for m3u8 URLs
            m3u8_pattern = r'(https?://[^"\']+\.m3u8[^"\'\s]*)'
            m3u8_matches = re.findall(m3u8_pattern, html_page.text)
            if m3u8_matches:
                if is_bait_source(m3u8_matches[0]):
                    logger.debug("Ignoring bait source: %s", m3u8_matches[0])
                else:
                    source_json = {"hls": m3u8_matches[0]}
                    logger.info("Found HLS URL: %s", m3u8_matches[0])

            # Look for mp4 URLs
            if not source_json:
                mp4_pattern = r'(https?://[^"\']+\.mp4[^"\'\s]*)'
                mp4_matches = re.findall(mp4_pattern, html_page.text)
                if mp4_matches:
                    if is_bait_source(mp4_matches[0]):
                        logger.debug("Ignoring bait source: %s", mp4_matches[0])
                    else:
                        source_json = {"mp4": mp4_matches[0]}
                        logger.info("Found MP4 URL: %s", mp4_matches[0])

        # Method 5: Look for base64 encoded sources
        if not source_json:
            base64_pattern = r"base64[,:]([A-Za-z0-9+/=]+)"
            base64_matches = re.findall(base64_pattern, html_page.text)
            for match in base64_matches:
                try:
                    decoded = base64.b64decode(match).decode("utf-8")
                    if ".mp4" in decoded:
                        source_json = {"mp4": decoded}
                        logger.info("Found base64 encoded MP4 URL")
                        break
                    if ".m3u8" in decoded:
                        source_json = {"hls": decoded}
                        logger.info("Found base64 encoded HLS URL")
                        break
                except (ValueError, KeyError, TypeError):
                    continue

        # Method 6: Look for a168c encoded sources
        if not source_json:
            logger.info("Searching for a168c encoded sources...")

            # Robust pattern to capture long base64 string inside script tags
            a168c_script_pattern = r"a168c\s*=\s*'([^']+)'"
            match = re.search(a168c_script_pattern, html_page.text, re.DOTALL)

            if match:
                raw_base64 = match.group(1)
                try:
                    cleaned = clean_base64(raw_base64)
                    decoded = base64.b64decode(cleaned).decode("utf-8")[::-1]

                    # Optional: Try parsing full JSON if applicable
                    try:
                        parsed = json.loads(decoded)
                        # print("[+] Decoded JSON:")
                        # print(json.dumps(parsed, indent=4))

                        if "direct_access_url" in parsed:
                            source_json = {"mp4": parsed["direct_access_url"]}
                            logger.info("Found direct .mp4 URL in JSON.")
                        elif "source" in parsed:
                            source_json = {"hls": parsed["source"]}
                            logger.info("Found fallback .m3u8 URL in JSON.")
                    except json.JSONDecodeError:
                        logger.warning(
                            "Decoded string is not valid JSON. Trying fallback regex search..."
                        )

                        # If it's not JSON, fallback to pattern search
                        mp4_match = re.search(
                            r'(https?://[^\s"]+\.mp4[^\s"]*)', decoded
                        )
                        m3u8_match = re.search(
                            r'(https?://[^\s"]+\.m3u8[^\s"]*)', decoded
                        )

                        if mp4_match:
                            source_json = {"mp4": mp4_match.group(1)}
                            logger.info("Found base64 encoded MP4 URL.")
                        elif m3u8_match:
                            source_json = {"hls": m3u8_match.group(1)}
                            logger.info("Found base64 encoded HLS (m3u8) URL.")
                except Exception:
                    logger.exception("Failed to decode a168c strings")

        # Method 7: Look for MKGMa encoded sources
        # https://github.com/p4ul17/voe-dl/issues/33#issuecomment-2807006973
        if not source_json:
            logger.info("Searching for MKGMa sources...")

            MKGMa_pattern = r'MKGMa="(.*?)"'
            match = re.search(MKGMa_pattern, html_page.text, re.DOTALL)

            if match:
                raw_MKGMa = match.group(1)

                def rot13_decode(s: str) -> str:
                    result = []
                    for c in s:
                        if "A" <= c <= "Z":
                            result.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
                        elif "a" <= c <= "z":
                            result.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
                        else:
                            result.append(c)
                    return "".join(result)

                def shift_characters(s: str, offset: int) -> str:
                    return "".join(chr(ord(c) - offset) for c in s)

                try:
                    step1 = rot13_decode(raw_MKGMa)
                    step2 = step1.replace("_", "")
                    step3 = base64.b64decode(step2).decode("utf-8")
                    step4 = shift_characters(step3, 3)
                    step5 = step4[::-1]

                    decoded = base64.b64decode(step5).decode("utf-8")

                    try:
                        parsed_json = json.loads(decoded)

                        if "direct_access_url" in parsed_json:
                            source_json = {"mp4": parsed_json["direct_access_url"]}
                            logger.info("Found direct .mp4 URL in JSON.")
                        elif "source" in parsed_json:
                            source_json = {"hls": parsed_json["source"]}
                            logger.info("Found fallback .m3u8 URL in JSON.")

                    except json.JSONDecodeError:
                        logger.warning(
                            "Decoded string is not valid JSON. Attempting fallback regex search..."
                        )

                        mp4_match = re.search(
                            r'(https?://[^\s"]+\.mp4[^\s"]*)', decoded
                        )
                        m3u8_match = re.search(
                            r'(https?://[^\s"]+\.m3u8[^\s"]*)', decoded
                        )

                        if mp4_match:
                            source_json = {"mp4": mp4_match.group(1)}
                            logger.info("Found base64 encoded MP4 URL.")
                        elif m3u8_match:
                            source_json = {"hls": m3u8_match.group(1)}
                            logger.info("Found base64 encoded HLS (m3u8) URL.")

                except (ValueError, TypeError, json.JSONDecodeError):
                    logger.exception("Error while decoding MKGMa string")

        # Method 8: Obfuscated JSON in <script type="application/json"> tags
        if not source_json:
            logger.info("Searching for obfuscated JSON sources…")
            app_json_scripts = soup.find_all(
                "script", attrs={"type": "application/json"}
            )
            for js in app_json_scripts:
                if not js.string:
                    continue
                candidate = js.string.strip()
                result = deobfuscate_embedded_json(candidate)
                if result is None:
                    continue
                try:
                    if isinstance(result, dict):
                        if "direct_access_url" in result:
                            source_json = {"mp4": result["direct_access_url"]}
                            logger.info("Found direct .mp4 URL in obfuscated JSON")
                        elif "source" in result:
                            source_json = {"hls": result["source"]}
                            logger.info("Found .m3u8 URL in obfuscated JSON")
                        elif any(k in result for k in ("mp4", "hls")):
                            source_json = result
                            logger.info("Found media URL in obfuscated JSON")
                    elif isinstance(result, str):
                        mp4_m = re.search(r'(https?://[^\s"]+\.mp4[^\s"]*)', result)
                        m3u8_m = re.search(r'(https?://[^\s"]+\.m3u8[^\s"]*)', result)
                        if mp4_m:
                            source_json = {"mp4": mp4_m.group(0)}
                        elif m3u8_m:
                            source_json = {"hls": m3u8_m.group(0)}
                        if source_json:
                            logger.info(
                                "Extracted media link from obfuscated JSON string"
                            )
                except (ValueError, TypeError, json.JSONDecodeError, AttributeError):
                    logger.exception("Error parsing obfuscated JSON result")
                if source_json:
                    break

        # If we still don't have sources, try to find any iframe that might contain the video
        if not source_json:
            iframes = soup.find_all("iframe")
            if iframes:
                for iframe in iframes:
                    iframe_src = iframe.get("src")
                    if iframe_src:
                        if iframe_src.startswith("//"):
                            iframe_src = "https:" + iframe_src
                        elif not iframe_src.startswith(("http://", "https://")):
                            # Handle relative URLs
                            parsed_url = urlparse(URL)
                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                            iframe_src = (
                                base_url + iframe_src
                                if iframe_src.startswith("/")
                                else base_url + "/" + iframe_src
                            )

                        logger.info("Found iframe, following to: %s", iframe_src)
                        return extract_voe(iframe_src)

        if not source_json:
            logger.warning(
                "Could not find sources in the page. The site structure might have changed."
            )
            logger.debug("Dumping page content for debugging...")
            with open(
                f"debug_page_{int(time.time())}.html", "w", encoding="utf-8"
            ) as f:
                f.write(html_page.text)
            logger.debug("Page content saved for debugging")
            return video_source_list

        # Process the found sources
        try:
            if isinstance(source_json, str):
                logger.warning("source_json is a string. Wrapping it in a dictionary.")
                source_json = {"mp4": source_json}

            if not isinstance(source_json, dict):
                logger.warning("Unexpected source_json format: %s", type(source_json))
                logger.debug("source_json content: %s", source_json)
                return video_source_list

            if "mp4" in source_json:
                link = source_json["mp4"]
                # Check if the link is base64 encoded
                if isinstance(link, str) and (
                    link.startswith("eyJ") or re.match(r"^[A-Za-z0-9+/=]+$", link)
                ):
                    try:
                        link = base64.b64decode(link).decode("utf-8")
                        logger.info("Successfully decoded base64 MP4 URL")
                    except (ValueError, TypeError, base64.binascii.Error):
                        logger.exception("Failed to decode base64")

                # Ensure the link is a complete URL
                if link.startswith("//"):
                    link = "https:" + link

                basename, ext = os.path.splitext(name)
                if not ext:
                    ext = ".mp4"
                name = f"{basename}_SS{ext}"

                logger.info("Found MP4 stream: %s", link)

                # Return VideoSource object instead of ydl_opts
                video_source = VideoSource(
                    url=link,
                    original_url=URL,
                    quality=quality,  # VOE doesn't specify quality
                    language=lang,
                    type=type_str,
                    host="voe",
                    requires_proxy=False,  # VOE doesn't need proxy
                    headers=headers,
                )
                video_source_list.append(video_source)
            elif "hls" in source_json:
                link = source_json["hls"]
                # Check if the link is base64 encoded
                if isinstance(link, str) and (
                    link.startswith("eyJ") or re.match(r"^[A-Za-z0-9+/=]+$", link)
                ):
                    try:
                        link = base64.b64decode(link).decode("utf-8")
                        logger.info("Successfully decoded base64 HLS URL")
                    except (ValueError, TypeError, base64.binascii.Error):
                        logger.exception("Failed to decode base64")

                # Ensure the link is a complete URL
                if link.startswith("//"):
                    link = "https:" + link

                basename, ext = os.path.splitext(name)
                if not ext:
                    ext = ".mp4"  # HLS streams are typically extract_voeed as MP4
                name = f"{basename}_SS{ext}"

                logger.info("Found HLS stream: %s", link)

                # Return VideoSource object instead of ydl_opts
                video_source = VideoSource(
                    url=link,
                    original_url=URL,
                    quality=quality,  # VOE doesn't specify quality
                    language=lang,
                    type=type_str,
                    host="voe",
                    requires_proxy=False,  # VOE doesn't need proxy
                    headers=headers,
                )
                video_source_list.append(video_source)
            else:
                logger.warning(
                    "Could not find extractable URL. The site might have changed."
                )
                logger.debug(
                    "Available keys in source_json: %s", list(source_json.keys())
                )
                for key, value in source_json.items():
                    logger.debug("%s: %s", key, value)
        except KeyError:
            logger.exception("KeyError")
            logger.warning(
                "Could not find extractable URL. The site might have changed."
            )
            logger.debug("Available keys in source_json: %s", list(source_json.keys()))

    except requests.exceptions.RequestException:
        logger.exception("Request error")

    # Removed print newline
    # Return empty list if no sources were found or error occurred
    return video_source_list


def is_bait_source(source: str) -> bool:
    """Return True if *source* looks like a known test/bait video."""
    bait_filenames = [
        "BigBuckBunny",
        "Big_Buck_Bunny_1080_10s_5MB",
        "bbb.mp4",
        # Add more bait filenames as needed
    ]
    bait_domains = [
        "test-videos.co.uk",
        "sample-videos.com",
        "commondatastorage.googleapis.com",
        # Add more bait domains as needed
    ]
    if any(fn.lower() in source.lower() for fn in bait_filenames):
        return True
    parsed = urlparse(source)
    return bool(any(dom in parsed.netloc for dom in bait_domains))


# Function to clean and pad base64 safely
def clean_base64(s):
    try:
        s = s.replace("\\", "")  # remove literal backslashes
        missing_padding = len(s) % 4
        if missing_padding:
            s += "=" * (4 - missing_padding)
        # Validate if the string is valid base64
        base64.b64decode(s, validate=True)
    except (base64.binascii.Error, ValueError):
        logger.exception("Invalid base64 string")
        return None
    return s
