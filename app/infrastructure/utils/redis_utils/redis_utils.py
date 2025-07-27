import json
from typing import Any, Union
import redis.asyncio as redis
from typing import AsyncGenerator
from app.infrastructure.config.config import settings


class RedisUtils:
    """
       Utility class for interacting with Redis.

       Provides methods for managing connections to a Redis instance and
       performing operations such as storing, retrieving, and deleting data,
       as well as managing message lists for chat rooms.
   """

    def __init__(self):
        """
           Initializes the Redis connection pool and sets up connection details.
       """
        self.redis_host = settings.redis_host
        self.redis_port = settings.redis_port
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}"
        self._pool = redis.ConnectionPool.from_url(self.redis_url)
        self._pubsub_client = redis.Redis.from_url(self.redis_url, decode_responses=True)

    async def publish(self, channel: str, message: dict) -> None:
        """
        Publishes a message to the specified channel.
        """
        await self._pubsub_client.publish(channel, json.dumps(message))

    async def psubscribe(self, pattern: str) -> AsyncGenerator[tuple[int, dict], None]:
        """
        Subscribes to all Redis channels matching the pattern and yields (room_id, message) pairs.
        """
        pubsub = self._pubsub_client.pubsub()
        await pubsub.psubscribe(pattern)

        try:
            async for message in pubsub.listen():
                if message["type"] != "pmessage":
                    continue

                channel = message["channel"]
                if isinstance(channel, bytes):
                    channel = channel.decode()

                try:
                    room_id = int(channel.split(":")[2])
                    payload = json.loads(message["data"])
                    yield room_id, payload
                except Exception:
                    continue
        finally:
            await pubsub.punsubscribe(pattern)
            await pubsub.close()

    async def pool_disconnect(self) -> None:
        """
            Closes the Redis connection pool.
        """
        await self._pool.aclose()

    async def get(self, key: str) -> Any:
        """
            Retrieves a value from Redis by its key.
        """
        client = redis.Redis.from_pool(self._pool)
        value = await client.get(key)
        await client.aclose()
        return value.decode()

    async def set(self, key: str, value: Any, expire: int = 60) -> None:
        """
            Stores a value in Redis with an optional expiration time.
        """
        client = redis.Redis.from_pool(self._pool)
        await client.set(key, value)
        await client.expire(key, expire)
        await client.aclose()

    async def add_message_to_list(self, room_id: int, messages: Union[dict, list[dict]]):
        """
        Adds one or multiple messages to the list of messages for a specific chat room.
        """
        client = redis.Redis.from_pool(self._pool)
        key = f"chat:room:{room_id}:messages"

        if isinstance(messages, dict):
            messages = [messages]

        json_messages = [json.dumps(message) for message in messages]
        if json_messages:
            await client.lpush(key, *json_messages)
            await client.ltrim(key, 0, 499)
            await client.expire(key, 10)

        await client.aclose()

    async def get_messages_list(self, room_id: int, start: int = 0, end: int = -1):
        """
            Retrieves messages from a chat room's message list.
        """
        client = redis.Redis.from_pool(self._pool)
        key = f"chat:room:{room_id}:messages"
        messages = await client.lrange(key, start, end)
        await client.aclose()
        return [json.loads(msg.decode()) for msg in messages]

    async def delete_all_messages(self, room_id: int) -> None:
        """
            Deletes all messages in a specific chat room's message list.
        """
        client = redis.Redis.from_pool(self._pool)
        key = f"chat:room:{room_id}:messages"

        await client.delete(key)
        await client.aclose()

    async def message_list_exists(self, room_id: int) -> bool:
        """
            Checks if a message list exists for a specific chat room.
        """
        client = redis.Redis.from_pool(self._pool)
        key = f"chat:room:{room_id}:messages"
        exists = await client.exists(key)
        await client.aclose()
        return exists == 1


redis_utils = RedisUtils()
