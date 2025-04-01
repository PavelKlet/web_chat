from typing import Any
import redis.asyncio as redis
from infrastructure.config import settings


class RedisUtils:
    def __init__(self):
        self.redis_host = settings.redis_host
        self.redis_port = settings.redis_port
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}"
        self._pool = redis.ConnectionPool.from_url(self.redis_url)

    async def pool_disconnect(self) -> None:
        await self._pool.aclose()

    async def get(self, key: str) -> Any:
        client = redis.Redis.from_pool(self._pool)
        value = await client.get(key)
        await client.aclose()
        return value.decode()

    async def set(self, key: str, value: Any, expire: int = 60) -> None:
        client = redis.Redis.from_pool(self._pool)
        await client.set(key, value)
        await client.expire(key, expire)
        await client.aclose()


redis_utils = RedisUtils()
