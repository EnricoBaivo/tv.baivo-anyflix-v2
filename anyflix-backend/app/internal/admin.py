"""Admin utilities and internal functionality."""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/sources/status")
async def get_sources_status():
    """Get status of all sources."""
    return {
        "sources": {
            "aniworld": {"status": "active", "type": "anime"},
            "serienstream": {"status": "active", "type": "series"},
        }
    }
