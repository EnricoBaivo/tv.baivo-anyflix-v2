import yt_dlp

from lib.models.base import VideoSource
from lib.utils.caching import ServiceCacheConfig, cached


def _get_quality_score(video_source: VideoSource) -> int:
    """
    Calculate quality score for sorting video sources.
    Higher score = better quality.
    """
    quality_id = str(video_source.quality).lower()

    # Combined formats with audio+video - HIGHEST PRIORITY (360p+)
    combined_formats = {
        "22": 3000,  # 720p MP4 (H.264 + AAC) - BEST COMBINED
        "18": 2900,  # 360p MP4 (H.264 + AAC)
        "43": 2800,  # 360p WebM (VP8 + Vorbis)
    }

    # M3U8 playlists - HIGH PRIORITY (360p+)
    m3u8_formats = {
        "96": 2700,  # 1080p HLS
        "95": 2600,  # 720p HLS - BEST M3U8
        "94": 2500,  # 480p HLS
        "93": 2400,  # 360p HLS
    }

    # Storyboard formats - LOW PRIORITY (for thumbnails)
    if quality_id.startswith("sb"):
        return 500

    # Check combined formats first
    if quality_id in combined_formats:
        return combined_formats[quality_id]

    # Check m3u8 formats
    if quality_id in m3u8_formats:
        return m3u8_formats[quality_id]

    return 100


def _is_storyboard(fmt: dict) -> bool:
    """
    Detect if a format is a storyboard/thumbnail preview.

    Args:
        fmt: Format dict from yt-dlp

    Returns:
        True if format is a storyboard
    """
    format_id = str(fmt.get("format_id", "")).lower()

    # Check format ID
    if format_id.startswith("sb"):
        return True

    # Check format note
    format_note = str(fmt.get("format_note", "")).lower()
    if "storyboard" in format_note:
        return True

    # Check extension (storyboards are typically mhtml or webp)
    ext = fmt.get("ext", "")
    if ext in ("mhtml", "webp"):
        return True

    return False


@cached(ttl=ServiceCacheConfig.EXTRACTOR_TTL, key_prefix="ytdlp_extract")
async def ytdlp_extractor(url: str, best_m3u8_only: bool = True) -> list[VideoSource]:
    """
    Extract video info using yt-dlp Python library.
    Returns best combined format (360p+), best m3u8 playlist, and storyboards.

    Args:
        url: YouTube or video URL
        best_m3u8_only: If True, only return the highest quality m3u8 (default: True)

    Returns:
        List of VideoSource objects sorted by quality (best first)
    """
    try:
        ydl_opts = {
            "quiet": False,
            "no_warnings": False,
            "extract_flat": False,
            "format": "best",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            sources: list[VideoSource] = []

            # Only include formats 360p and above
            COMBINED_FORMATS = {"22", "18", "43"}  # 720p, 360p, 360p WebM
            M3U8_FORMATS = {"93", "94", "95", "96"}  # 360p+, 480p, 720p, 1080p

            # Check main format first
            if info and "url" in info:
                video_url = info["url"]
                quality = info.get("format_id", "unknown")

                is_m3u8 = ".m3u8" in str(video_url)
                is_combined = quality in COMBINED_FORMATS

                if is_m3u8 or is_combined:
                    source_format = "m3u8" if is_m3u8 else "combined"

                    source = VideoSource(
                        url=video_url,
                        original_url=url,
                        quality=quality,
                        format=source_format,
                        host="ytdlp",
                        requires_proxy=False,
                        headers=None,
                        subtitles=None,
                        audios=None,
                    )
                    sources.append(source)

            # Filter all available formats
            if info and "formats" in info:
                for fmt in info["formats"]:
                    if not fmt.get("url"):
                        continue

                    format_id = fmt.get("format_id", "")
                    url_str = str(fmt["url"])

                    # Check if it's a storyboard
                    is_storyboard = _is_storyboard(fmt)

                    # Check if it's m3u8 or combined
                    is_m3u8 = ".m3u8" in url_str and format_id in M3U8_FORMATS
                    is_combined = format_id in COMBINED_FORMATS

                    # Only include: high-quality m3u8, combined formats, or storyboards
                    if not (is_m3u8 or is_combined or is_storyboard):
                        continue

                    # Set format field (not type!)
                    source_format = (
                        "storyboard"
                        if is_storyboard
                        else "m3u8"
                        if is_m3u8
                        else "combined"
                    )

                    source = VideoSource(
                        url=fmt["url"],
                        original_url=url,
                        quality=format_id,
                        format=source_format,
                        host="ytdlp",
                        requires_proxy=False,
                        headers=None,
                        subtitles=None,
                        audios=None,
                    )
                    sources.append(source)

            # Remove duplicates
            seen_urls = set()
            unique_sources = []
            for source in sources:
                if source.url not in seen_urls:
                    seen_urls.add(source.url)
                    unique_sources.append(source)

            # Sort by quality (best first)
            unique_sources.sort(key=_get_quality_score, reverse=True)

            # Filter to keep only best m3u8 if requested
            if best_m3u8_only:
                filtered_sources = []
                m3u8_added = False

                for source in unique_sources:
                    if source.format == "m3u8":
                        if not m3u8_added:
                            filtered_sources.append(source)  # Keep only the best m3u8
                            m3u8_added = True
                    else:
                        filtered_sources.append(source)  # Keep all non-m3u8

                unique_sources = filtered_sources

            return unique_sources

    except yt_dlp.DownloadError as e:
        print(f"yt-dlp download error: {e}")
        return []
    except (ValueError, RuntimeError, OSError) as e:
        print(f"yt-dlp extraction failed: {e}")
        return []
