import asyncio

from app.application.services.websocket.websocket_manager import WebsocketManager
from app.infrastructure.utils.redis_utils.redis_utils import RedisUtils


async def start_listener(
    redis_utils: RedisUtils,
    websocket_manager: WebsocketManager,
) -> None:
    """
    Global Redis Pub/Sub listener across all rooms.
    """
    async for room_id, payload in redis_utils.psubscribe("chat:room:*:channel"):
        msg_type = payload.get("type", "chat_message")

        if msg_type == "chat_message":
            await websocket_manager.broadcast_to_room(room_id, payload)

        elif msg_type == "chat_update":
            await websocket_manager.broadcast_chat_update(payload)

async def start_listener_with_restart(
        redis_utils: RedisUtils,
        websocket_manager: WebsocketManager
) -> None:
    while True:
        try:
            await start_listener(redis_utils, websocket_manager)
        except Exception as e:
            print(f"Listener crashed with error: {e}. Restarting in 5 seconds...")
            await asyncio.sleep(5)
