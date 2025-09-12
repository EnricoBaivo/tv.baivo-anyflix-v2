"""FastAPI dependencies for the streaming media backend service."""

from lib.services.media_service import MediaService

from .internal.proxy import VideoProxyService


def get_media_service() -> MediaService:
    """Get basic media service instance for streaming content."""
    return MediaService(enable_metadata=False)


def get_enhanced_media_service() -> MediaService:
    """Get enhanced media service instance with AniList metadata enrichment."""
    return MediaService(enable_metadata=True)


# Backward compatibility aliases
def get_anime_service() -> MediaService:
    """Get basic media service instance (backward compatibility)."""
    return get_media_service()


def get_enhanced_anime_service() -> MediaService:
    """Get enhanced media service instance (backward compatibility)."""
    return get_enhanced_media_service()


def get_proxy_service() -> VideoProxyService:
    """Get video proxy service instance."""
    return VideoProxyService()
