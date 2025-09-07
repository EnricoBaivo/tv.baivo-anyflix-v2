"""Video proxy API router."""

import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..dependencies import get_proxy_service
from ..internal.proxy import VideoProxyService

router = APIRouter(prefix="/proxy", tags=["proxy"])


@router.get("/stream")
async def proxy_video_stream(
    request: Request,
    url: str = Query(..., description="Video URL to proxy"),
    proxy_service: VideoProxyService = Depends(get_proxy_service),
):
    """Proxy video stream with custom headers.

    Args:
        url: The video URL to proxy
        h_{header_name}: Custom headers (e.g., h_Referer=https://example.com)

    Example:
        /proxy/stream?url=https://example.com/video.mp4&h_Referer=https://aniworld.to&h_User-Agent=CustomUA
    """
    try:
        # Extract custom headers from query parameters
        custom_headers = {}
        for param, value in request.query_params.items():
            if param.startswith("h_") and param != "h_url":
                header_name = param[2:]  # Remove "h_" prefix
                custom_headers[header_name] = urllib.parse.unquote(value)

        # Get request headers
        request_headers = dict(request.headers)

        # Get range header for video seeking
        range_header = request_headers.get("range")

        async with proxy_service:
            return await proxy_service.proxy_video_stream(
                video_url=url,
                custom_headers=custom_headers,
                request_headers=request_headers,
                range_header=range_header,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")


@router.get("/m3u8")
async def proxy_m3u8_playlist(
    request: Request,
    url: str = Query(..., description="M3U8 playlist URL to proxy"),
    proxy_service: VideoProxyService = Depends(get_proxy_service),
):
    """Proxy M3U8 playlist and rewrite URLs.

    Args:
        url: The M3U8 playlist URL to proxy
        h_{header_name}: Custom headers (e.g., h_Referer=https://vidmoly.to)

    Example:
        /proxy/m3u8?url=https://example.com/playlist.m3u8&h_Referer=https://vidmoly.to
    """
    try:
        # Extract custom headers from query parameters
        custom_headers = {}
        for param, value in request.query_params.items():
            if param.startswith("h_") and param != "h_url":
                header_name = param[2:]  # Remove "h_" prefix
                custom_headers[header_name] = urllib.parse.unquote(value)

        # Build base proxy URL for rewriting
        base_url = str(request.base_url).rstrip("/")

        async with proxy_service:
            return await proxy_service.proxy_m3u8_playlist(
                playlist_url=url, custom_headers=custom_headers, base_proxy_url=base_url
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"M3U8 proxy error: {str(e)}")


@router.get("/info")
async def get_video_info(
    url: str = Query(..., description="Video URL to check"),
    proxy_service: VideoProxyService = Depends(get_proxy_service),
):
    """Get video information without downloading.

    Args:
        url: The video URL to check
        h_{header_name}: Custom headers

    Returns:
        Video information including availability and metadata
    """
    try:
        # Extract custom headers (same pattern as other endpoints)
        # For simplicity, we'll add this if needed

        async with proxy_service:
            info = await proxy_service.get_video_info(url)
            return info

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Info error: {str(e)}")


# OPTIONS handler for CORS preflight
@router.options("/{path:path}")
async def proxy_options(path: str):
    """Handle CORS preflight requests for proxy endpoints."""
    return {"status": "ok"}
