"""M3U8 playlist extractor."""

import re
from typing import Any, Dict, List, Optional

from ..models.base import VideoSource
from ..utils.client import HTTPClient
from ..utils.js_utils import abs_url


async def m3u8_extractor(
    url: str, headers: Optional[Dict[str, str]] = None
) -> List[VideoSource]:
    """
    Extract video sources from M3U8 playlist.
    Based on the JavaScript m3u8Extractor function.
    """
    # Define attribute lists for parsing M3U8
    stream_attributes = [
        ("avg_bandwidth", r"AVERAGE-BANDWIDTH=(\d+)"),
        ("bandwidth", r"\bBANDWIDTH=(\d+)"),
        ("resolution", r"\bRESOLUTION=([\dx]+)"),
        ("framerate", r"\bFRAME-RATE=([\d\.]+)"),
        ("codecs", r'\bCODECS="(.*?)"'),
        ("video", r'\bVIDEO="(.*?)"'),
        ("audio", r'\bAUDIO="(.*?)"'),
        ("subtitles", r'\bSUBTITLES="(.*?)"'),
        ("captions", r'\bCLOSED-CAPTIONS="(.*?)"'),
    ]

    media_attributes = [
        ("type", r"\bTYPE=([\w-]*)"),
        ("group", r'\bGROUP-ID="(.*?)"'),
        ("lang", r'\bLANGUAGE="(.*?)"'),
        ("name", r'\bNAME="(.*?)"'),
        ("autoselect", r"\bAUTOSELECT=(\w*)"),
        ("default", r"\bDEFAULT=(\w*)"),
        ("instream-id", r'\bINSTREAM-ID="(.*?)"'),
        ("assoc-lang", r'\bASSOC-LANGUAGE="(.*?)"'),
        ("channels", r'\bCHANNELS="(.*?)"'),
        ("uri", r'\bURI="(.*?)"'),
    ]

    streams = []
    videos = {}
    audios = {}
    subtitles = {}
    captions = {}
    dict_map = {
        "VIDEO": videos,
        "AUDIO": audios,
        "SUBTITLES": subtitles,
        "CLOSED-CAPTIONS": captions,
    }

    # Fetch M3U8 content
    client = HTTPClient()
    try:
        response = await client.get(url, headers=headers)
        text = response.body

        if response.status_code != 200:
            print(f"Failed to fetch M3U8 content: {response.status_code}")
            return []
    except Exception as e:
        print(f"Failed to fetch M3U8 content: {e}")
        return []

    # Collect media
    for match in re.finditer(r"#EXT-X-MEDIA:(.*)", text):
        info = match.group(1)
        medium = {}

        for attr_name, pattern in media_attributes:
            m = re.search(pattern, info)
            medium[attr_name] = m.group(1) if m else None

        media_type = medium.get("type")
        group = medium.get("group")

        if media_type and group:
            # Remove type and group from medium dict
            medium = {k: v for k, v in medium.items() if k not in ["type", "group"]}

            type_dict = dict_map.get(media_type, {})
            if group not in type_dict:
                type_dict[group] = []
            type_dict[group].append(medium)

    # Collect streams
    for match in re.finditer(r"#EXT-X-STREAM-INF:(.*)\s*(.*)", text):
        info = match.group(1)
        stream_url = match.group(2).strip()

        stream = {"url": abs_url(stream_url, url)}

        for attr_name, pattern in stream_attributes:
            m = re.search(pattern, info)
            stream[attr_name] = m.group(1) if m else None

        # Add media references
        stream["video"] = videos.get(stream.get("video"))
        stream["audio"] = audios.get(stream.get("audio"))
        stream["subtitles"] = subtitles.get(stream.get("subtitles"))
        stream["captions"] = captions.get(stream.get("captions"))

        # Format quality from resolution or bandwidth
        quality = ""
        if stream.get("resolution"):
            resolution_match = re.search(r"x(\d+)", stream["resolution"])
            if resolution_match:
                quality = resolution_match.group(1) + "p"
        else:
            bandwidth_value = stream.get("avg_bandwidth") or stream.get("bandwidth")
            if bandwidth_value:
                bandwidth = int(bandwidth_value)
                quality = f"{bandwidth / 1000000:.1f}Mb/s"

        # Extract subtitles and audio tracks
        subs = None
        if stream.get("subtitles"):
            subs = [
                {"file": s.get("uri"), "label": s.get("name")}
                for s in stream["subtitles"]
                if s.get("uri")
            ]

        audios_list = None
        if stream.get("audio"):
            audios_list = [
                {"file": a.get("uri"), "label": a.get("name")}
                for a in stream["audio"]
                if a.get("uri")
            ]

        video_source = VideoSource(
            url=stream["url"],
            original_url=stream["url"],
            quality=quality,
            headers=headers,
            subtitles=subs,
            audios=audios_list,
        )
        streams.append(video_source)

    # If no streams found, return the original URL as a video source
    if not streams:
        return [
            VideoSource(
                url=url,
                original_url=url,
                quality="",
                headers=headers,
                subtitles=None,
                audios=None,
            )
        ]

    return streams
