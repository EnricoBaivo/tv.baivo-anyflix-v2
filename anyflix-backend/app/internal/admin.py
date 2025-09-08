"""Admin utilities and internal functionality."""

from fastapi import APIRouter

from ..dependencies import get_anime_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/sources/status")
async def get_sources_status():
    """Get status of all available sources."""
    from lib.services.anime_service import AnimeService

    anime_service = AnimeService()
    sources = anime_service.get_available_sources()

    return {
        "sources": sources,
        "total_count": len(sources),
        "status": "active",
    }
