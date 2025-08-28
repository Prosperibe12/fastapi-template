import threading
import asyncio
from abc import ABCMeta 
from typing import Optional

import aioredis

from backend.core.config import settings

class SingletonMeta(ABCMeta):
    """
    Create a thread-safe singleton metaclass.
    """
    _instances = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
    
class RedisConnection(metaclass=SingletonMeta):
    """
    Class for managing redis connection.
    This ensures that only one instance of the Redis connection exists
    """
    def __init__(self):
        """
        prevent re-initialization when the singleton metaclass returns an existing instance
        """
        if not hasattr(self, '_initialized'):
            self._redis: Optional[aioredis.Redis] = None
            self._initialized = False
            self._init_lock = asyncio.Lock()
    
    async def __call__(self) -> aioredis.Redis:
        if not self._initialized:
            async with self._init_lock:
                if not self._initialized: 
                    self._redis = aioredis.from_url(
                        str(settings.redis_dsn),
                        encoding="utf-8",
                        decode_responses=True,
                    )
                    self._initialized = True
        return self._redis
    
    async def close(self):
        """Close the Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._initialized = False
    
    @classmethod
    async def close_all_instances(cls):
        """Close all instances - useful for cleanup"""
        for instance in cls._instances.values():
            if hasattr(instance, 'close'):
                await instance.close()
                
redis_conn = RedisConnection()