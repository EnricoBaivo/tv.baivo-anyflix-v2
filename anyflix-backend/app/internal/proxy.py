"""Video proxy service for handling video streams with custom headers."""

import logging
from typing import Dict, Optional

import httpx
from fastapi import HTTPException, Request, Response
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


class VideoProxyService:
    """Service for proxying video streams with custom headers."""

    def __init__(self):
        """Initialize video proxy service."""
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, read=300.0),  # Extended read timeout for video
            follow_redirects=True,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, read=300.0),
                follow_redirects=True,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )
        return self._client

    async def proxy_video_stream(
        self,
        video_url: str,
        custom_headers: Optional[Dict[str, str]] = None,
        request_headers: Optional[Dict[str, str]] = None,
        range_header: Optional[str] = None,
    ) -> StreamingResponse:
        """Proxy video stream with custom headers.

        Args:
            video_url: The actual video URL to proxy
            custom_headers: Custom headers required by the video host
            request_headers: Headers from the original request
            range_header: Range header for partial content requests

        Returns:
            StreamingResponse with the video stream
        """
        logger.info(f"Proxying video stream: {video_url}")
        logger.debug(f"Custom headers: {custom_headers}")
        logger.debug(f"Range header: {range_header}")

        # Prepare headers for the upstream request
        upstream_headers = {}

        # Add custom headers (from VideoSource)
        if custom_headers:
            upstream_headers.update(custom_headers)

        # Add standard video streaming headers
        upstream_headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "identity",  # Don't compress video streams
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "video",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site",
            }
        )

        # Handle range requests for video seeking
        if range_header:
            upstream_headers["Range"] = range_header

        # Forward some client headers if available
        if request_headers:
            for header in ["Origin", "Referer"]:
                if header.lower() in request_headers:
                    upstream_headers[header] = request_headers[header.lower()]

        try:
            logger.debug(f"Making upstream request with headers: {upstream_headers}")

            # Make request to the actual video URL using async context manager
            async with self.client.stream(
                "GET", video_url, headers=upstream_headers
            ) as response:
                logger.info(f"Upstream response status: {response.status_code}")
                logger.debug(f"Upstream response headers: {dict(response.headers)}")

                # Check for error status codes
                if response.status_code >= 400:
                    error_msg = f"Upstream server returned {response.status_code}"
                    logger.error(f"{error_msg} for URL: {video_url}")

                    # Provide user-friendly error messages
                    if response.status_code == 403:
                        detail = "Video source access denied. The video may require specific headers or authentication."
                    elif response.status_code == 404:
                        detail = "Video not found. The URL may be expired or invalid."
                    elif response.status_code == 429:
                        detail = "Too many requests. Please try again later."
                    elif response.status_code >= 500:
                        detail = "Video source server error. Please try again later."
                    else:
                        detail = f"Video source error: {response.status_code}"

                    raise HTTPException(status_code=502, detail=detail)

                # Prepare response headers
                response_headers = {}

                # Copy essential headers from upstream
                for header in [
                    "content-type",
                    "content-range",
                    "accept-ranges",
                ]:
                    if header in response.headers:
                        response_headers[header] = response.headers[header]

                # Only copy content-length for non-streaming responses
                if "content-length" in response.headers and response.status_code != 200:
                    response_headers["content-length"] = response.headers[
                        "content-length"
                    ]

                # Add CORS headers
                response_headers.update(
                    {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                        "Access-Control-Allow-Headers": "Range, Content-Type, Authorization",
                        "Access-Control-Expose-Headers": "Content-Length, Content-Range, Accept-Ranges",
                        "Cache-Control": "public, max-age=3600",
                    }
                )

                # Handle different response types
                if response.status_code == 206:  # Partial content
                    response_headers["Accept-Ranges"] = "bytes"

                async def stream_generator():
                    """Generator for streaming video data."""
                    try:
                        bytes_streamed = 0
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            bytes_streamed += len(chunk)
                            yield chunk

                        logger.info(
                            f"Successfully streamed {bytes_streamed} bytes for {video_url}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error during streaming for {video_url}: {str(e)}"
                        )
                        # Don't re-raise streaming errors, just log them
                        return

                return StreamingResponse(
                    stream_generator(),
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response.headers.get("content-type", "video/mp4"),
                )

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while proxying {video_url}: {str(e)}")
            raise HTTPException(status_code=408, detail="Video stream timeout")
        except httpx.RequestError as e:
            logger.error(f"Request error while proxying {video_url}: {str(e)}")
            raise HTTPException(
                status_code=502, detail=f"Failed to proxy video: {str(e)}"
            )
        except HTTPException:
            # Re-raise HTTPExceptions without wrapping
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while proxying {video_url}: {str(e)}", exc_info=True
            )
            raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

    async def proxy_m3u8_playlist(
        self,
        playlist_url: str,
        custom_headers: Optional[Dict[str, str]] = None,
        base_proxy_url: str = "",
    ) -> Response:
        """Proxy M3U8 playlist and rewrite URLs to use the proxy.

        Args:
            playlist_url: The M3U8 playlist URL
            custom_headers: Custom headers for the request
            base_proxy_url: Base URL for the proxy service

        Returns:
            Response with the modified M3U8 playlist
        """
        logger.info(f"Proxying M3U8 playlist: {playlist_url}")
        logger.debug(f"Custom headers: {custom_headers}")
        logger.debug(f"Base proxy URL: {base_proxy_url}")

        # Prepare headers
        upstream_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
        }

        if custom_headers:
            upstream_headers.update(custom_headers)

        try:
            logger.debug(f"Fetching M3U8 playlist with headers: {upstream_headers}")

            # Fetch the M3U8 playlist
            response = await self.client.get(playlist_url, headers=upstream_headers)

            logger.info(f"M3U8 playlist response status: {response.status_code}")

            if response.status_code != 200:
                error_msg = f"Failed to fetch M3U8 playlist: {response.status_code}"
                logger.error(f"{error_msg} for URL: {playlist_url}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_msg,
                )

            # Parse and rewrite M3U8 content
            playlist_content = response.text
            base_url = "/".join(playlist_url.split("/")[:-1]) + "/"

            logger.debug(f"Base URL for rewriting: {base_url}")
            logger.debug(f"Original playlist content length: {len(playlist_content)}")

            # Rewrite relative URLs to absolute URLs through our proxy
            lines = playlist_content.split("\n")
            rewritten_lines = []
            url_count = 0

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # This is a URL line
                    if not line.startswith("http"):
                        # Relative URL - make it absolute
                        absolute_url = base_url + line
                    else:
                        # Already absolute
                        absolute_url = line

                    # Rewrite to use our proxy
                    if base_proxy_url:
                        proxied_url = (
                            f"{base_proxy_url}/proxy/stream?url={absolute_url}"
                        )
                        # Add headers as query params if needed
                        if custom_headers:
                            import urllib.parse

                            header_params = "&".join(
                                [
                                    f"h_{k}={urllib.parse.quote(v)}"
                                    for k, v in custom_headers.items()
                                ]
                            )
                            proxied_url += f"&{header_params}"
                        rewritten_lines.append(proxied_url)
                        url_count += 1
                    else:
                        rewritten_lines.append(absolute_url)
                        url_count += 1
                else:
                    rewritten_lines.append(line)

            rewritten_content = "\n".join(rewritten_lines)

            logger.info(f"Rewritten M3U8 playlist with {url_count} URLs")
            logger.debug(f"Rewritten content length: {len(rewritten_content)}")

            return Response(
                content=rewritten_content,
                media_type="application/vnd.apple.mpegurl",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                    "Cache-Control": "public, max-age=300",
                },
            )

        except httpx.RequestError as e:
            logger.error(f"Request error while fetching M3U8 {playlist_url}: {str(e)}")
            raise HTTPException(
                status_code=502, detail=f"Failed to fetch M3U8: {str(e)}"
            )
        except HTTPException:
            # Re-raise HTTPExceptions without wrapping
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while proxying M3U8 {playlist_url}: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail=f"M3U8 proxy error: {str(e)}")

    async def get_video_info(
        self, video_url: str, custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Get video information without streaming the full content.

        Args:
            video_url: Video URL to check
            custom_headers: Custom headers for the request

        Returns:
            Dictionary with video information
        """
        logger.info(f"Getting video info for: {video_url}")
        logger.debug(f"Custom headers: {custom_headers}")

        upstream_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        if custom_headers:
            upstream_headers.update(custom_headers)

        try:
            logger.debug(f"Making HEAD request with headers: {upstream_headers}")

            # Make a HEAD request to get info without downloading
            response = await self.client.head(video_url, headers=upstream_headers)

            logger.info(f"Video info response status: {response.status_code}")
            logger.debug(f"Video info response headers: {dict(response.headers)}")

            info = {
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length"),
                "accept_ranges": response.headers.get("accept-ranges"),
                "last_modified": response.headers.get("last-modified"),
                "available": response.status_code == 200,
            }

            logger.info(f"Video info result: {info}")
            return info

        except Exception as e:
            logger.error(
                f"Error getting video info for {video_url}: {str(e)}", exc_info=True
            )
            return {
                "status_code": 0,
                "available": False,
                "error": str(e),
            }
