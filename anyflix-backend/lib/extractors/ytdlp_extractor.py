from typing import List

import yt_dlp

from ..models.base import VideoSource


def ytdlp_extractor(url: str) -> List[VideoSource]:
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
            sources = []

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

            return sources

    except yt_dlp.DownloadError as e:
        print(f"yt-dlp download error: {e}")
        return []
    except Exception as e:
        print(f"yt-dlp extraction failed: {e}")
        return []
