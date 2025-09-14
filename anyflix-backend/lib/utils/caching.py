"""Caching utilities for API services."""

import hashlib
import logging
import pickle
import re
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from aiocache import caches, redis

logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])

# Cache configuration - will be initialized dynamically
CACHE_CONFIG = {}


class PydanticSerializer:
    """Custom serializer for Pydantic models that handles complex objects better."""

    # Required by aiocache
    encoding = None

    def dumps(self, value):
        """Serialize value to bytes."""
        # Handle None values explicitly
        if value is None:
            return pickle.dumps(None)

        if hasattr(value, "model_dump"):
            # Pydantic v2
            serializable_data = {
                "_pydantic_class": value.__class__.__module__
                + "."
                + value.__class__.__name__,
                "_pydantic_data": value.model_dump(),
            }
        elif hasattr(value, "dict"):
            # Pydantic v1
            serializable_data = {
                "_pydantic_class": value.__class__.__module__
                + "."
                + value.__class__.__name__,
                "_pydantic_data": value.dict(),
            }
        else:
            # Not a Pydantic model, use regular serialization
            serializable_data = value

        return pickle.dumps(serializable_data)

    def loads(self, value):
        """Deserialize bytes to value."""
        # Handle None/empty values
        if value is None:
            return None

        try:
            data = pickle.loads(value)
        except Exception as e:
            logger.warning("Failed to unpickle data: %s", e)
            return None

        if isinstance(data, dict) and "_pydantic_class" in data:
            # This was a Pydantic model, reconstruct it
            class_path = data["_pydantic_class"]
            module_name, class_name = class_path.rsplit(".", 1)

            try:
                # Import the module and get the class
                module = __import__(module_name, fromlist=[class_name])
                model_class = getattr(module, class_name)

                # Reconstruct the Pydantic model
                return model_class(**data["_pydantic_data"])
            except Exception as e:
                logger.warning(
                    f"Failed to reconstruct Pydantic model {class_path}: {e}"
                )
                # Return None to force cache miss and re-execution
                logger.info("Invalidating cache entry due to deserialization failure")
                return None

        return data


# Initialize cache with configuration
def initialize_cache(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0,
    redis_password: str = "",
) -> None:
    """Initialize cache configuration.

    Args:
        redis_host: Redis host
        redis_port: Redis port
        redis_db: Redis database number
        redis_password: Redis password
    """
    global CACHE_CONFIG

    # Build Redis configuration
    redis_config = {
        "default": {
            "cache": "aiocache.RedisCache",
            "endpoint": redis_host,
            "port": redis_port,
            "db": redis_db,
            "timeout": 1,
            "serializer": {"class": "lib.utils.caching.PydanticSerializer"},
            "plugins": [
                {"class": "aiocache.plugins.HitMissRatioPlugin"},
                {"class": "aiocache.plugins.TimingPlugin"},
            ],
        }
    }

    # Add password if provided
    if redis_password:
        redis_config["default"]["password"] = redis_password

    CACHE_CONFIG = redis_config

    try:
        caches.set_config(CACHE_CONFIG)
        logger.info(
            f"Redis cache initialized successfully at {redis_host}:{redis_port}"
        )
    except Exception as e:
        logger.warning(
            "Failed to initialize Redis cache, falling back to memory: %s", e
        )
        # Fallback to memory cache if Redis is not available
        fallback_config = {
            "default": {
                "cache": "aiocache.SimpleMemoryCache",
                "serializer": {"class": "lib.utils.caching.PydanticSerializer"},
            }
        }
        caches.set_config(fallback_config)
        logger.info("Memory cache initialized as fallback")


# Cache key generation
def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a human-readable cache key from function arguments with endpoint-based namespacing.

    Args:
        prefix: Cache key prefix (usually function name)
        *args: Function positional arguments
        **kwargs: Function keyword arguments

    Returns:
        str: Generated human-readable cache key with namespace
    """
    # Determine the endpoint namespace based on the prefix
    namespace = _get_endpoint_namespace(prefix)

    # Create a human-readable string from arguments
    key_parts = [prefix]

    # Add positional arguments (skip 'self' for instance methods)
    for i, arg in enumerate(args):
        # Skip 'self' parameter for instance methods
        # Check if this is actually an instance (not built-in types like str, int, etc.)
        if (
            i == 0
            and hasattr(arg, "__class__")
            and hasattr(arg.__class__, "__name__")
            and not isinstance(
                arg, (str, int, float, bool, list, tuple, dict, type(None))
            )
        ):
            continue

        # Convert argument to readable string
        readable_arg = _make_readable_arg(arg)
        if readable_arg:
            key_parts.append(readable_arg)

    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        readable_value = _make_readable_arg(value)
        if readable_value:
            key_parts.append(f"{key}={readable_value}")

    # Join parts with underscores and clean up for Redis key compatibility
    key_string = "_".join(key_parts)

    # Clean up the key to be Redis-compatible and readable
    # Replace problematic characters and limit length
    key_string = re.sub(
        r"[^\w\-=.]", "_", key_string
    )  # Replace non-alphanumeric with underscore
    key_string = re.sub(r"_+", "_", key_string)  # Collapse multiple underscores
    key_string = key_string.strip("_")  # Remove leading/trailing underscores

    # If key is too long, truncate but keep it readable
    if len(key_string) > 200:
        # Keep prefix and truncate the rest, but add a short hash for uniqueness
        prefix_part = key_parts[0]
        remaining = "_".join(key_parts[1:])
        short_hash = hashlib.md5(remaining.encode()).hexdigest()[:8]
        key_string = f"{prefix_part}_{short_hash}"

    # Combine namespace with the key using Redis folder-like structure
    return f"{namespace}:{key_string}" if namespace else key_string


def _get_endpoint_namespace(prefix: str) -> str:
    """Determine the endpoint namespace based on the cache key prefix.

    Args:
        prefix: Cache key prefix

    Returns:
        str: Endpoint namespace for organizing keys in Redis
    """
    # Map cache prefixes to endpoint namespaces
    endpoint_mappings = {
        # AniWorld provider endpoints
        "aniworld_popular": "endpoints:aniworld:popular",
        "aniworld_latest": "endpoints:aniworld:latest",
        "aniworld_search": "endpoints:aniworld:search",
        "aniworld_detail": "endpoints:aniworld:series:detail",
        "aniworld_videos": "endpoints:aniworld:videos",
        # SerienStream provider endpoints
        "serienstream_popular": "endpoints:serienstream:popular",
        "serienstream_latest": "endpoints:serienstream:latest",
        "serienstream_search": "endpoints:serienstream:search",
        "serienstream_detail": "endpoints:serienstream:series:detail",
        "serienstream_videos": "endpoints:serienstream:videos",
        # AniList service endpoints
        "anilist_search_anime": "services:anilist:search:anime",
        "anilist_search_media": "services:anilist:search:media",
        "anilist_media_by_id": "services:anilist:media:by_id",
        "anilist_trending_anime": "services:anilist:trending:anime",
        "anilist_popular_anime": "services:anilist:popular:anime",
        # TMDB service endpoints
        "tmdb_configuration": "services:tmdb:configuration",
        "tmdb_search_multi": "services:tmdb:search:multi",
        "tmdb_movie_details": "services:tmdb:movie:details",
        "tmdb_tv_details": "services:tmdb:tv:details",
        "tmdb_search_and_match": "services:tmdb:search:match",
        "tmdb_find_external": "services:tmdb:find:external",
        "tmdb_image_url": "services:tmdb:image:url",
        # Extractor endpoints
        "dood_extract": "extractors:dood:extract",
        "vidmoly_extract": "extractors:vidmoly:extract",
        "vidoza_extract": "extractors:vidoza:extract",
        "voe_extract": "extractors:voe:extract",
        "filemoon_extract": "extractors:filemoon:extract",
        "luluvdo_extract": "extractors:luluvdo:extract",
        "speedfiles_extract": "extractors:speedfiles:extract",
        "ytdlp_extract": "extractors:ytdlp:extract",
    }

    return endpoint_mappings.get(prefix, f"cache:{prefix}")


def _make_readable_arg(arg) -> str:
    """Convert an argument to a readable string for cache keys.

    Args:
        arg: Argument to convert

    Returns:
        str: Human-readable representation
    """
    if arg is None:
        return "none"
    if isinstance(arg, bool):
        return "true" if arg else "false"
    if isinstance(arg, (int, float)):
        return str(arg)
    if isinstance(arg, str):
        # Clean and truncate strings
        clean_str = re.sub(
            r"[^\w\s-]", "", arg
        )  # Remove special chars except spaces and hyphens
        clean_str = re.sub(
            r"\s+", "_", clean_str.strip()
        )  # Replace spaces with underscores
        return clean_str[:50] if clean_str else "empty"  # Limit length
    if isinstance(arg, (list, tuple)):
        if len(arg) == 0:
            return "empty_list"
        if len(arg) <= 3:
            # Show small lists
            readable_items = [_make_readable_arg(item) for item in arg]
            return f"[{','.join(readable_items)}]"
        # Show first few items for large lists
        readable_items = [_make_readable_arg(item) for item in arg[:2]]
        return f"[{','.join(readable_items)}_and_{len(arg) - 2}_more]"
    if isinstance(arg, dict):
        if len(arg) == 0:
            return "empty_dict"
        if len(arg) <= 2:
            # Show small dicts
            items = [f"{k}={_make_readable_arg(v)}" for k, v in sorted(arg.items())]
            return f"{{{','.join(items)}}}"
        # Show first few items for large dicts
        items = sorted(arg.items())[:2]
        readable_items = [f"{k}={_make_readable_arg(v)}" for k, v in items]
        return f"{{{','.join(readable_items)}_and_{len(arg) - 2}_more}}"
    if hasattr(arg, "__dict__"):
        # For objects, use class name and key attributes
        class_name = arg.__class__.__name__
        if hasattr(arg, "name"):
            return f"{class_name}_{_make_readable_arg(arg.name)}"
        if hasattr(arg, "id"):
            return f"{class_name}_{arg.id}"
        return class_name.lower()
    # Fallback to string representation, cleaned
    str_repr = str(arg)
    clean_str = re.sub(r"[^\w]", "_", str_repr)
    return clean_str[:30] if clean_str else "unknown"


# Cache decorator
def cached(
    ttl: int = 3600,  # 1 hour default
    key_prefix: str | None = None,
    cache_name: str = "default",
    skip_cache_on_error: bool = True,
) -> Callable[[F], F]:
    """Decorator to cache async function results.

    Args:
        ttl: Time to live in seconds (default: 1 hour)
        key_prefix: Custom key prefix (defaults to function name)
        cache_name: Cache instance name
        skip_cache_on_error: Whether to skip cache on errors

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if caching is enabled globally
            try:
                from app.config import settings

                if not settings.enable_caching:
                    logger.debug(
                        f"Caching disabled globally, executing function directly: {func.__name__}"
                    )
                    return await func(*args, **kwargs)
                logger.debug(
                    f"Caching enabled globally, executing function with caching: {func.__name__}"
                )
            except ImportError:
                logger.warning(
                    f"Failed to import settings: {e}, continuing with caching"
                )
                # If we can't import settings, assume caching is enabled (backward compatibility)

            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Get cache instance
            cache = caches.get(cache_name)

            try:
                # Try to get from cache first
                try:
                    cached_result = await cache.get(cache_key)
                    if cached_result is not None:
                        logger.debug("Cache hit for key: %s", cache_key)
                        return cached_result
                except Exception as cache_get_error:
                    logger.warning(
                        f"Failed to retrieve from cache for key {cache_key}: {cache_get_error}"
                    )
                    # Continue to execute function if cache retrieval fails

                logger.debug("Cache miss for key: %s", cache_key)

                # Execute function and cache result
                result = await func(*args, **kwargs)

                # Only cache non-None results to avoid serialization errors
                if result is not None:
                    try:
                        # Store in cache (serializer will handle Pydantic models automatically)
                        await cache.set(cache_key, result, ttl=ttl)
                        logger.debug(
                            f"Cached result for key: {cache_key} (TTL: {ttl}s)"
                        )
                    except Exception as cache_set_error:
                        logger.warning(
                            f"Failed to cache result for key {cache_key}: {cache_set_error}"
                        )
                        # Don't fail the request if caching fails
                else:
                    logger.debug("Skipping cache for None result: %s", cache_key)

                return result

            except (redis.RedisError, pickle.PickleError, ValueError):
                logger.exception("Cache error for key %s", cache_key)
                if skip_cache_on_error:
                    # Execute function without caching on error
                    return await func(*args, **kwargs)
                raise

        return wrapper

    return decorator


# Cache management functions
class CacheManager:
    """Cache management utilities."""

    def __init__(self, cache_name: str = "default") -> None:
        self.cache = caches.get(cache_name)

    async def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with a specific prefix or namespace.

        Args:
            prefix: Key prefix to clear (can be endpoint namespace like 'endpoints:aniworld:*'
                   or cache prefix like 'aniworld_popular')

        Returns:
            Number of keys cleared
        """
        try:
            # Check if this is a Redis cache
            if self.cache.__class__.__name__ == "RedisCache":
                # Get Redis connection
                conn = self.cache.get_connection()

                try:
                    # If prefix looks like a namespace path, use it directly
                    if ":" in prefix:
                        search_pattern = (
                            f"{prefix}*" if not prefix.endswith("*") else prefix
                        )
                    else:
                        # If it's a cache prefix, find the corresponding namespace
                        namespace = _get_endpoint_namespace(prefix)
                        search_pattern = f"{namespace}:*"

                    keys = await conn.client.keys(search_pattern)
                    if keys:
                        deleted = await conn.client.delete(*keys)
                        logger.info(
                            f"Cleared {deleted} cache keys matching pattern: {search_pattern}"
                        )
                        await self.cache.release_conn(conn)
                        return deleted

                    await self.cache.release_conn(conn)
                    return 0

                except (redis.RedisError, pickle.PickleError, ValueError):
                    await self.cache.release_conn(conn)
                    raise

            else:
                # For memory cache, try to clear all (limited functionality)
                await self.cache.clear()
                logger.info("Cleared all cache entries (memory cache)")
                return 1  # Return 1 to indicate some action was taken

        except Exception:
            logger.exception("Failed to clear cache prefix %s", prefix)
            return 0

    async def clear_endpoint(self, endpoint_path: str) -> int:
        """Clear all cache keys for a specific endpoint.

        Args:
            endpoint_path: Endpoint path like 'aniworld/popular' or 'anilist/search'

        Returns:
            Number of keys cleared
        """
        # Convert endpoint path to namespace pattern
        if endpoint_path.startswith("aniworld/"):
            namespace = (
                f"endpoints:aniworld:{endpoint_path.split('/', 1)[1].replace('/', ':')}"
            )
        elif endpoint_path.startswith("serienstream/"):
            namespace = f"endpoints:serienstream:{endpoint_path.split('/', 1)[1].replace('/', ':')}"
        elif endpoint_path.startswith("anilist/"):
            namespace = (
                f"services:anilist:{endpoint_path.split('/', 1)[1].replace('/', ':')}"
            )
        elif endpoint_path.startswith("tmdb/"):
            namespace = (
                f"services:tmdb:{endpoint_path.split('/', 1)[1].replace('/', ':')}"
            )
        else:
            namespace = f"endpoints:{endpoint_path.replace('/', ':')}"

        return await self.clear_prefix(f"{namespace}:*")

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            stats = {}

            # Check if this is a Redis cache
            if self.cache.__class__.__name__ == "RedisCache":
                try:
                    # Get Redis connection
                    conn = self.cache.get_connection()

                    # Get Redis info through the client
                    info = await conn.client.info()

                    stats = {
                        "cache_type": "redis",
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory": info.get("used_memory", 0),
                        "used_memory_human": info.get("used_memory_human", "0B"),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0),
                        "total_commands_processed": info.get(
                            "total_commands_processed", 0
                        ),
                        "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                    }

                    # Calculate hit ratio
                    hits = stats["keyspace_hits"]
                    misses = stats["keyspace_misses"]
                    total = hits + misses
                    if total > 0:
                        stats["hit_ratio"] = round(hits / total * 100, 2)
                    else:
                        stats["hit_ratio"] = 0

                    # Get key count
                    try:
                        keys = await conn.client.keys("*")
                        stats["total_keys"] = len(keys) if keys else 0

                        # Count keys by namespace
                        namespace_counts = {}
                        if keys:
                            for key in keys:
                                if isinstance(key, bytes):
                                    key = key.decode("utf-8")
                                if ":" in key:
                                    namespace = key.split(":", 1)[0]
                                    namespace_counts[namespace] = (
                                        namespace_counts.get(namespace, 0) + 1
                                    )
                        stats["namespaces"] = namespace_counts

                    except Exception as e:
                        logger.warning("Failed to get key statistics: %s", e)
                        stats["total_keys"] = "unknown"
                        stats["namespaces"] = {}

                    # Release connection
                    await self.cache.release_conn(conn)

                except Exception as e:
                    logger.exception("Failed to get Redis stats: %s", e)
                    stats = {"cache_type": "redis", "error": str(e)}

            else:
                # Memory cache or other type
                stats = {
                    "cache_type": self.cache.__class__.__name__.lower(),
                    "note": "Limited statistics available for non-Redis cache",
                }

            return stats
        except Exception as e:
            logger.exception("Failed to get cache stats: %s", e)
            return {"error": str(e)}

    async def flush_all(self) -> bool:
        """Flush all cache entries.

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.cache.clear()
            logger.info("Flushed all cache entries")
            return True
        except Exception as e:
            logger.exception("Failed to flush cache: %s", e)
            return False


# Specific cache configurations for different data types
class ServiceCacheConfig:
    """Cache configuration for different service types."""

    # AniList cache settings
    ANILIST_SEARCH_TTL = 1800  # 30 minutes
    ANILIST_MEDIA_TTL = 3600  # 1 hour
    ANILIST_TRENDING_TTL = 900  # 15 minutes

    # TMDB cache settings
    TMDB_SEARCH_TTL = 1800  # 30 minutes
    TMDB_DETAILS_TTL = 7200  # 2 hours
    TMDB_CONFIG_TTL = 86400  # 24 hours

    # Provider cache settings
    PROVIDER_POPULAR_TTL = 900  # 15 minutes
    PROVIDER_LATEST_TTL = 600  # 10 minutes
    PROVIDER_VIDEOS_TTL = 3600  # 1 hour

    # Extractor cache settings
    EXTRACTOR_TTL = 3600  # 1 hour - cache video extraction results
    PROVIDER_SEARCH_TTL = 1800  # 30 minutes
    PROVIDER_DETAIL_TTL = 3600  # 1 hour


# Cache warming utilities
async def warm_cache_for_popular_content():
    """Warm cache with popular content."""
    logger.info("Starting cache warming for popular content...")
    # This could be implemented to pre-populate cache with popular anime/series


# Cache will be initialized by the application startup
