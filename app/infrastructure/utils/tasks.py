import asyncio
from typing import Dict, List
from starlette.websockets import WebSocket

from app.infrastructure.utils.redis_utils.redis_utils import RedisUtils


async def start_listener(
    redis_utils: RedisUtils,
    rooms: Dict[int, Dict[str, List[WebSocket]]],
    delete_room_callback
) -> None:
    """
    Global Redis Pub/Sub listener across all rooms.
    Sends incoming messages to all WebSocket connections in rooms[room_id]["connections"].
    """

    async for room_id, payload in redis_utils.psubscribe("chat:room:*:channel"):
        connections = rooms.get(room_id, {}).get("connections", [])

        if not connections:
            await delete_room_callback(room_id)
            continue

        for ws in connections[:]:
            try:
                await ws.send_json(payload)
            except Exception:
                connections.remove(ws)

        if not connections:
            await delete_room_callback(room_id)


async def start_listener_with_restart(redis_utils, rooms, delete_room_callback):
    while True:
        try:
            await start_listener(redis_utils, rooms, delete_room_callback)
        except Exception as e:
            print(f"Listener crashed with error: {e}. Restarting in 5 seconds...")
            await asyncio.sleep(5)
