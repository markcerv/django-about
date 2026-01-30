"""Cache statistics utilities for django-about."""

import logging

logger = logging.getLogger(__name__)


def get_cache_stats():
    """
    Gather cache statistics.
    Returns a dictionary with cache information (read-only, no clearing).
    Returns None if cache backend is not available or not Redis.
    """
    cache_stats = {
        "backend": None,
        "total_keys": None,
        "used_memory": None,
        "max_memory": None,
        "error": None,
    }

    try:
        from django.core.cache import cache
        from django.conf import settings

        # Get cache backend name
        cache_backend = settings.CACHES.get("default", {}).get("BACKEND", "Unknown")
        cache_stats["backend"] = (
            cache_backend.split(".")[-1] if cache_backend else "Unknown"
        )

        # Try to get Redis-specific statistics
        try:
            from django_redis import get_redis_connection

            redis_conn = get_redis_connection("default")

            # Get cache memory info
            info = redis_conn.info()
            cache_stats["used_memory"] = info.get("used_memory_human", "N/A")
            cache_stats["max_memory"] = info.get("maxmemory_human", "N/A")
            cache_stats["total_keys"] = redis_conn.dbsize()

            # Additional useful Redis info
            cache_stats["redis_version"] = info.get("redis_version")
            cache_stats["connected_clients"] = info.get("connected_clients")
            cache_stats["uptime_days"] = info.get("uptime_in_days")

        except ImportError:
            # django-redis not installed, try generic cache operations
            logger.debug("django-redis not available, cache stats limited")
            cache_stats["backend_note"] = "Limited stats (not Redis backend)"
        except Exception as e:
            # Not using Redis or connection error
            logger.debug(f"Could not get Redis-specific stats: {e}")
            cache_stats["backend_note"] = "Redis connection not available"

    except Exception as e:
        cache_stats["error"] = str(e)
        logger.warning(f"Error getting cache statistics: {e}")

    # Return None if we couldn't get any useful stats
    if cache_stats["backend"] == "Unknown" and cache_stats["error"]:
        return None

    return cache_stats


def get_cache_backend_name():
    """Get the name of the configured cache backend."""
    try:
        from django.conf import settings

        cache_backend = settings.CACHES.get("default", {}).get("BACKEND", "Unknown")
        return cache_backend.split(".")[-1] if cache_backend else "Unknown"
    except Exception as e:
        logger.warning(f"Error getting cache backend name: {e}")
        return "Error"
