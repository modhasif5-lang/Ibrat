"""
Redis caching client for Product Service and Recommendation Engine.
Provides non-blocking async cache operations with automatic serialization and graceful fallback.
"""

import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisCacheService:
    """Async Redis cache manager for recommendation and catalog caching."""

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.client: Optional[aioredis.Redis] = None
        self._connected: bool = False

    async def connect(self):
        """Establish Redis connection pool."""
        try:
            self.client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            await self.client.ping()
            self._connected = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self._connected = False
            logger.warning(f"Redis connection deferred (server offline): {e}")

    async def disconnect(self):
        """Close connection pool."""
        if self.client and self._connected:
            await self.client.close()
            self._connected = False
            logger.info("Redis connection closed.")

    async def is_healthy(self) -> bool:
        """Check Redis connectivity."""
        if not self.client:
            return False
        try:
            return bool(await self.client.ping())
        except Exception:
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """Fetch and deserialize JSON from Redis cache."""
        if not self.client or not self._connected:
            return None
        try:
            val = await self.client.get(key)
            if val:
                return json.loads(val)
            return None
        except Exception as e:
            logger.debug(f"Redis cache GET failed for {key}: {e}")
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Serialize and store JSON in Redis cache with TTL."""
        if not self.client or not self._connected:
            return False
        try:
            serialized = json.dumps(value, default=str)
            await self.client.set(key, serialized, ex=ttl_seconds)
            return True
        except Exception as e:
            logger.debug(f"Redis cache SET failed for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Invalidate a specific cache key."""
        if not self.client or not self._connected:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception:
            return False


cache_service = RedisCacheService()
