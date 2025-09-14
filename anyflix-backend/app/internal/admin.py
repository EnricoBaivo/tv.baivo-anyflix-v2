"""Admin utilities and internal functionality."""

from typing import Any

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
async def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    try:
        from lib.utils.caching import CacheManager

        cache_manager = CacheManager()
        stats = await cache_manager.get_cache_stats()
    except (ImportError, RuntimeError, ValueError) as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache stats: {e!s}"
        ) from e
    else:
        return {
            "cache_enabled": True,
            "stats": stats,
            "status": "active" if stats else "unavailable",
        }


@router.post("/cache/clear/{prefix}")
async def clear_cache_prefix(prefix: str) -> dict[str, Any]:
    """Clear cache entries with specific prefix.

    Args:
        prefix: Cache key prefix to clear (e.g., 'anilist_search', 'tmdb_details', 'endpoints:aniworld:*')
    """
    try:
        from lib.utils.caching import CacheManager

        cache_manager = CacheManager()
        cleared_count = await cache_manager.clear_prefix(prefix)
    except (ImportError, RuntimeError, ValueError) as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear cache: {e!s}"
        ) from e
    else:
        return {
            "message": f"Cleared {cleared_count} cache entries with prefix '{prefix}'",
            "prefix": prefix,
            "cleared_count": cleared_count,
        }


@router.post("/cache/clear/endpoint/{endpoint_path:path}")
async def clear_cache_endpoint(endpoint_path: str) -> dict[str, Any]:
    """Clear cache entries for a specific endpoint.

    Args:
        endpoint_path: Endpoint path to clear (e.g., 'aniworld/popular', 'anilist/search')
    """
    try:
        from lib.utils.caching import CacheManager

        cache_manager = CacheManager()
        cleared_count = await cache_manager.clear_endpoint(endpoint_path)
    except (ImportError, RuntimeError, ValueError) as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear endpoint cache: {e!s}"
        ) from e
    else:
        return {
            "message": f"Cleared {cleared_count} cache entries for endpoint '{endpoint_path}'",
            "endpoint": endpoint_path,
            "cleared_count": cleared_count,
        }


@router.post("/cache/flush")
async def flush_cache() -> dict[str, Any]:
    """Flush all cache entries."""

    def _raise_flush_error() -> None:
        raise HTTPException(status_code=500, detail="Failed to flush cache")

    try:
        from lib.utils.caching import CacheManager

        cache_manager = CacheManager()
        success = await cache_manager.flush_all()
    except (ImportError, RuntimeError, ValueError) as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to flush cache: {e!s}"
        ) from e
    else:
        if success:
            return {"message": "All cache entries flushed successfully"}
        _raise_flush_error()
