import yt_dlp

from lib.models.base import VideoSource
from lib.utils.caching import ServiceCacheConfig, cached


def _get_quality_score(video_source) -> int:
    """
    Calculate quality score for sorting video sources.
    Higher score = better quality.

    Args:
        video_source: VideoSource object

    Returns:
        Quality score (higher is better)
    """
    quality_id = str(video_source.quality).lower()

    # High resolution video formats (DASH/HLS compatible) - HIGHEST PRIORITY
    high_res_video_formats = {
        "137": 2000,  # 1080p MP4 (H.264 video only) - BEST QUALITY
        "248": 1950,  # 1080p WebM (VP9 video only)
        "136": 1900,  # 720p MP4 (H.264 video only)
        "247": 1850,  # 720p WebM (VP9 video only)
        "22": 1800,  # 720p MP4 (H.264 + AAC) - Combined but lower priority than 1080p
        "135": 1700,  # 480p MP4 (H.264 video only)
        "244": 1650,  # 480p WebM (VP9 video only)
    }

    # Medium resolution formats
    medium_res_formats = {
        "134": 1000,  # 360p MP4 (H.264 video only)
        "243": 950,  # 360p WebM (VP9 video only)
        "18": 900,  # 360p MP4 (H.264 + AAC) - Combined
        "133": 800,  # 240p MP4 (H.264 video only)
        "242": 750,  # 240p WebM (VP9 video only)
        "43": 700,  # 360p WebM (VP8 + Vorbis)
    }

    # Low resolution formats
    low_res_formats = {
        "160": 500,  # 144p MP4 (H.264 video only)
        "278": 450,  # 144p WebM (VP9 video only)
        "36": 400,  # 320p 3GPP
        "17": 350,  # 144p 3GPP
    }

    # Audio-only formats (lower priority)
    audio_only_formats = {
        "251": 200,  # ~160k Opus audio
        "140": 190,  # 128k AAC audio
        "250": 180,  # ~70k Opus audio
        "249": 170,  # ~50k Opus audio
    }

    # Check high resolution formats first (highest priority)
    if quality_id in high_res_video_formats:
        return high_res_video_formats[quality_id]

    # Check medium resolution formats
    if quality_id in medium_res_formats:
        return medium_res_formats[quality_id]

    # Check low resolution formats
    if quality_id in low_res_formats:
        return low_res_formats[quality_id]

    # Check audio-only formats
    if quality_id in audio_only_formats:
        return audio_only_formats[quality_id]

    # Handle adaptive formats (394-399, etc.)
    if quality_id.startswith(("394", "395", "396", "397", "398", "399")):
        return 300  # Medium priority for adaptive VP9

    # Handle DRC (Dynamic Range Compression) formats
    if quality_id.endswith("-drc"):
        base_quality = quality_id.replace("-drc", "")
        base_score = _get_quality_score_by_id(base_quality)
        return (
            base_score - 50 if base_score > 0 else 100
        )  # Slightly lower than original

    # Handle storyboard formats (sb0, sb1, sb2) - lowest priority
    if quality_id.startswith("sb"):
        return 50

    # Unknown formats get medium-low priority
    return 100


def _get_quality_score_by_id(quality_id: str) -> int:
    """Helper function to get score by quality ID."""
    all_formats = {
        # High resolution (DASH/HLS compatible)
        "137": 2000,  # 1080p MP4 (H.264 video only)
        "248": 1950,  # 1080p WebM (VP9 video only)
        "136": 1900,  # 720p MP4 (H.264 video only)
        "247": 1850,  # 720p WebM (VP9 video only)
        "22": 1800,  # 720p MP4 (H.264 + AAC)
        "135": 1700,  # 480p MP4 (H.264 video only)
        "244": 1650,  # 480p WebM (VP9 video only)
        # Medium resolution
        "134": 1000,  # 360p MP4 (H.264 video only)
        "243": 950,  # 360p WebM (VP9 video only)
        "18": 900,  # 360p MP4 (H.264 + AAC)
        "133": 800,  # 240p MP4 (H.264 video only)
        "242": 750,  # 240p WebM (VP9 video only)
        "43": 700,  # 360p WebM (VP8 + Vorbis)
        # Low resolution
        "160": 500,  # 144p MP4 (H.264 video only)
        "278": 450,  # 144p WebM (VP9 video only)
        "36": 400,  # 320p 3GPP
        "17": 350,  # 144p 3GPP
        # Audio only
        "251": 200,  # ~160k Opus audio
        "140": 190,  # 128k AAC audio
        "250": 180,  # ~70k Opus audio
        "249": 170,  # ~50k Opus audio
    }
    return all_formats.get(quality_id, 0)


@cached(ttl=ServiceCacheConfig.EXTRACTOR_TTL, key_prefix="ytdlp_extract")
async def ytdlp_extractor(url: str) -> list[VideoSource]:
    """Extract video info using yt-dlp Python library."""
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "format": "best",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Extract video sources from yt-dlp info
            sources: list[VideoSource] = []

            if info and "url" in info:
                # Get the main video URL
                video_url = info["url"]
                quality = info.get("format_id", "unknown")

                # Create VideoSource object
                source = VideoSource(
                    url=video_url,
                    original_url=url,
                    quality=quality,
                    host="ytdlp",
                    requires_proxy=False,  # ytdlp sources don't need proxy
                    headers=None,
                    subtitles=None,
                    audios=None,
                )
                sources.append(source)

            # Check for multiple formats if available
            if info and "formats" in info:
                for fmt in info["formats"]:
                    if fmt.get("url"):
                        source = VideoSource(
                            url=fmt["url"],
                            original_url=url,
                            quality=fmt.get("format_id", "unknown"),
                            host="ytdlp",
                            requires_proxy=False,  # ytdlp sources don't need proxy
                            headers=None,
                            subtitles=None,
                            audios=None,
                        )
                        sources.append(source)

            # Sort sources by quality (best first)
            sources.sort(key=_get_quality_score, reverse=True)
            return sources

    except yt_dlp.DownloadError as e:
        print(f"yt-dlp download error: {e}")
        return []
    except Exception as e:
        print(f"yt-dlp extraction failed: {e}")
        return []
