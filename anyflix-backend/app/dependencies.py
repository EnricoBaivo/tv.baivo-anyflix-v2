"""FastAPI dependencies for the anime backend service."""

from lib.services.anime_service import AnimeService

from .internal.proxy import VideoProxyService


def get_anime_service() -> AnimeService:
    """Get basic anime service instance."""
    return AnimeService(enable_metadata=False)


def get_enhanced_anime_service() -> AnimeService:
    """Get enhanced anime service instance with AniList metadata."""
    return AnimeService(enable_metadata=True)


def get_proxy_service() -> VideoProxyService:
    """Get video proxy service instance."""
    return VideoProxyService()
