"""FastAPI dependencies for the anime backend service."""

from lib.services.anime_service import AnimeService

from .internal.proxy import VideoProxyService


def get_anime_service() -> AnimeService:
    """Get anime service instance."""
    return AnimeService()


def get_proxy_service() -> VideoProxyService:
    """Get video proxy service instance."""
    return VideoProxyService()
