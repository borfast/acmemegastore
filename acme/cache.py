# coding=utf-8
from abc import ABCMeta, abstractmethod

from aioredis import Redis


class AbstractCache(metaclass=ABCMeta):
    """Abstract base class for cache backends."""

    @abstractmethod
    async def has(self, key: str) -> bool:
        """Check if the given key is present in the cache."""

    @abstractmethod
    async def get(self, key: str) -> str:
        """Get the value for the given key from the cache."""

    @abstractmethod
    async def set(self, key: str, value: str):
        """Set the value for the given key on the cache."""

    @abstractmethod
    async def delete(self, key: str):
        """Delete the value for the given key from the cache."""


class RedisCache(AbstractCache):
    """Ridiculously simple cache using Redis as a storage medium."""

    def __init__(self, redis: Redis, expiration: int):
        self.redis = redis
        self.expiration = expiration

    async def has(self, key: str) -> bool:
        return await self.redis.exists(key)

    async def get(self, key: str) -> str:
        """Let's make life easier and return an already decoded string."""
        result = await self.redis.get(key)
        return result.decode('utf-8')

    async def set(self, key: str, value: str):
        return await self.redis.set(key, value, expire=self.expiration)

    async def delete(self, key: str):
        return await self.redis.delete(key)


class MemoryCache(AbstractCache):
    """Very simple memory cache, implemented just for use in tests."""
    def __init__(self):
        self._cache = {}

    async def has(self, key: str) -> bool:
        result = key in self._cache
        return result

    async def get(self, key: str) -> str:
        return self._cache.get(key)

    async def set(self, key: str, value: str):
        self._cache[key] = value

    async def delete(self, key: str):
        del self._cache[key]
