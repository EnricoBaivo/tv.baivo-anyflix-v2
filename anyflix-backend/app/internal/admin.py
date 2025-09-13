"""Admin utilities and internal functionality."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

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


@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    try:
        from lib.utils.caching import CacheManager

        cache_manager = CacheManager()
        stats = await cache_manager.get_cache_stats()
        return {
            "cache_enabled": True,
            "stats": stats,
            "status": "active" if stats else "unavailable",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache stats: {str(e)}"
        )


@router.post("/cache/clear/{prefix}")
async def clear_cache_prefix(prefix: str) -> Dict[str, Any]:
    """Clear cache entries with specific prefix.

    Args:
        prefix: Cache key prefix to clear (e.g., 'anilist_search', 'tmdb_details', 'endpoints:aniworld:*')
    """
    try:
        from lib.utils.caching import CacheManager

        cache_manager = CacheManager()
        cleared_count = await cache_manager.clear_prefix(prefix)
        return {
            "message": f"Cleared {cleared_count} cache entries with prefix '{prefix}'",
            "prefix": prefix,
            "cleared_count": cleared_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.post("/cache/clear/endpoint/{endpoint_path:path}")
async def clear_cache_endpoint(endpoint_path: str) -> Dict[str, Any]:
    """Clear cache entries for a specific endpoint.

    Args:
        endpoint_path: Endpoint path to clear (e.g., 'aniworld/popular', 'anilist/search')
    """
    try:
        from lib.utils.caching import CacheManager

        cache_manager = CacheManager()
        cleared_count = await cache_manager.clear_endpoint(endpoint_path)
        return {
            "message": f"Cleared {cleared_count} cache entries for endpoint '{endpoint_path}'",
            "endpoint": endpoint_path,
            "cleared_count": cleared_count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear endpoint cache: {str(e)}"
        )


@router.post("/cache/flush")
async def flush_cache() -> Dict[str, Any]:
    """Flush all cache entries."""
    try:
        from lib.utils.caching import CacheManager

        cache_manager = CacheManager()
        success = await cache_manager.flush_all()
        if success:
            return {"message": "All cache entries flushed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to flush cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to flush cache: {str(e)}")
