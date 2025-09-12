"""Admin utilities and internal functionality."""

from fastapi import APIRouter

from ..dependencies import get_anime_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/sources/status")
async def get_sources_status():
    """Get status of all available streaming media sources."""
    from lib.services.media_service import MediaService

    media_service = MediaService()
    sources = media_service.get_available_sources()

    return {
        "sources": sources,
        "total_count": len(sources),
        "status": "active",
    }
