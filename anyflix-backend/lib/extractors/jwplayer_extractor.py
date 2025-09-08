"""JWPlayer extractor."""

import json
import re
from typing import Dict, List, Optional

from ..models.base import VideoSource
from ..utils.cryptoaes.js_unpacker import JsUnpacker
from .m3u8_extractor import m3u8_extractor


async def jwplayer_extractor(
    text: str, headers: Optional[Dict[str, str]] = None
) -> List[VideoSource]:
    """
    Extract video sources from JWPlayer setup.
    Based on the JavaScript jwplayerExtractor function.
    """
    videos = []
    subtitles = []

    # Regex patterns to find JWPlayer setup
    setup_pattern = r"setup\(({[\s\S]*?})\)"
    sources_pattern = r"sources:\s*(\[[\s\S]*?\])"
    tracks_pattern = r"tracks:\s*(\[[\s\S]*?\])"

    # Try to unpack JavaScript if it's obfuscated
    unpacked_text = JsUnpacker().unpack_and_combine(text)
    # Try to extract data from setup first
    data = None
    setup_match = re.search(setup_pattern, text) or re.search(
        setup_pattern, unpacked_text
    )
    if setup_match:
        print(f"Found setup match: {setup_match.group(1)}")
        try:
            # Clean up the matched string and parse as JSON
            setup_str = setup_match.group(1)
            # Handle JavaScript object notation to JSON
            setup_str = _js_object_to_json(setup_str)
            print(f"Setup string: {setup_str}")
            data = json.loads(setup_str)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing setup string: {e}")
            data = None
        print(f"Data: {data}")
    if data:
        sources = data.get("sources", [])
        tracks = data.get("tracks", [])
    else:
        # Try to extract sources and tracks separately
        sources = (
            _extract_array(text, sources_pattern)
            or _extract_array(unpacked_text, sources_pattern)
            or []
        )
        tracks = (
            _extract_array(text, tracks_pattern)
            or _extract_array(unpacked_text, tracks_pattern)
            or []
        )

    # Process tracks (subtitles/captions)
    for track in tracks:
        if isinstance(track, dict) and track.get("type") == "captions":
            file_url = track.get("file")
            label = track.get("label", "Unknown")
            if file_url:
                subtitles.append({"file": file_url, "label": label})

    # Process sources
    for source in sources:
        if not isinstance(source, dict):
            continue

        file_url = source.get("file")
        if not file_url:
            continue

        if "master.m3u8" in file_url:
            # Extract from M3U8 playlist
            m3u8_videos = await m3u8_extractor(file_url, headers)
            videos.extend(m3u8_videos)
        elif ".mpd" in file_url:
            # DASH manifest - not implemented yet
            pass
        else:
            # Direct video file
            quality = source.get("label", "")
            video_source = VideoSource(
                url=file_url, original_url=file_url, quality=quality, headers=headers
            )
            videos.append(video_source)

    # Add subtitles to all video sources
    for video in videos:
        if video.subtitles is None:
            video.subtitles = subtitles
        elif subtitles:
            # Merge with existing subtitles
            existing_files = {sub["file"] for sub in video.subtitles or []}
            for sub in subtitles:
                if sub["file"] not in existing_files:
                    if video.subtitles is None:
                        video.subtitles = []
                    video.subtitles.append(sub)

    return videos


def _js_object_to_json(js_obj: str) -> str:
    """
    Convert JavaScript object notation to JSON.
    This is a simplified converter that handles basic cases.
    """
    # Replace unquoted keys with quoted keys, but avoid URLs
    # Use negative lookbehind to avoid matching protocol schemes like "https:"
    js_obj = re.sub(r'(?<!["\'\/])\b(\w+):', r'"\1":', js_obj)

    # Replace single quotes with double quotes, but preserve URLs inside quotes
    js_obj = re.sub(r"'([^']*)'", r'"\1"', js_obj)

    # Handle undefined and null
    js_obj = re.sub(r"\bundefined\b", "null", js_obj)
    print(f"JS object to JSON: {js_obj}")
    return js_obj


def _extract_array(text: str, pattern: str) -> Optional[List]:
    """Extract and parse array from text using regex pattern."""
    match = re.search(pattern, text)
    if not match:
        return None

    try:
        array_str = match.group(1)
        # Convert JS array to JSON
        array_str = _js_object_to_json(array_str)
        return json.loads(array_str)
    except (json.JSONDecodeError, ValueError):
        return None
