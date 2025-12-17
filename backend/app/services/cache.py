"""Redis cache service for API response caching."""
import json
from datetime import datetime
from typing import Any, Optional
from redis import Redis
from redis.exceptions import RedisError
from loguru import logger

from app.core.config import settings


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CacheService:
    """Service for caching API responses in Redis."""

    def __init__(self) -> None:
        """Initialize Redis client."""
        try:
            self.redis = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis.ping()
            logger.info(f"Cache service connected to Redis: {settings.redis_url}")
        except RedisError as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache will be disabled.")
            self.redis = None  # type: ignore

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if not self.redis:
            return None

        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            return False

        try:
            serialized = json.dumps(value, cls=DateTimeEncoder)
            self.redis.setex(key, ttl, serialized)
            return True
        except (RedisError, TypeError) as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            return False

        try:
            self.redis.delete(key)
            return True
        except RedisError as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Redis key pattern (e.g., "stories:*")

        Returns:
            Number of keys deleted
        """
        if not self.redis:
            return 0

        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Cache delete pattern error for '{pattern}': {e}")
            return 0

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            return False

        try:
            self.redis.flushdb()
            return True
        except RedisError as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def health_check(self) -> dict[str, Any]:
        """
        Check cache service health.

        Returns:
            Health status dictionary
        """
        if not self.redis:
            return {
                "status": "unhealthy",
                "message": "Redis client not initialized",
                "connected": False,
            }

        try:
            self.redis.ping()
            info = self.redis.info("stats")
            return {
                "status": "healthy",
                "message": "Cache service operational",
                "connected": True,
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except RedisError as e:
            return {
                "status": "unhealthy",
                "message": f"Redis connection failed: {e}",
                "connected": False,
            }


# Global cache service instance
cache_service = CacheService()
