import asyncio
from typing import Tuple, List, Optional

from fastapi import WebSocket, HTTPException

from app.application.services.auth.auth_manager import AuthManager
from app.infrastructure.models.relational.rooms import Room
from app.application.services.chat import ChatService
from app.application.services.user import UserService
from app.infrastructure.models.relational.users import User
from app.infrastructure.utils.redis_utils.redis_utils import RedisUtils, redis_utils

class WebsocketManager:
    """
        A class responsible for managing WebSocket connections, handling connections,
        sending messages in the chat, and caching messages in Redis.
    """

    def __init__(self, redis: RedisUtils):
        self.redis_utils = redis
        self.rooms = {}
        self.listener_tasks: dict[int, asyncio.Task] = {}

    async def start_listener(self, room_id: int) -> None:
        """
         Starts a message listener from Redis Pub/Sub for a specific room.
         Sends each message to all active WebSocket's in that room.
        """
        async for message in self.redis_utils.subscribe(f"chat:room:{room_id}:channel"):
            connections = self.rooms.get(room_id, {}).get("connections", [])

            if not connections:
                await self.delete_room(room_id)
                break

            for ws in connections[:]:
                try:
                    await ws.send_json(message)
                except Exception:
                    connections.remove(ws)

            if not connections:
                await self.delete_room(room_id)
                break

    async def connect(
            self,
            websocket: WebSocket,
            user_id_recipient: int,
            chat_service: ChatService,
            user_service: UserService,
            auth_manager: AuthManager
    ) -> Optional[Tuple[List[WebSocket], Room, User, User]]:

        """
            Establishes a WebSocket connection, authenticates the user via token,
            finds or creates a chat room, and sends the message history from Redis or the database.
        """

        await websocket.accept()

        try:
            access_token = await websocket.receive_text()
            user = await auth_manager.get_user(token=access_token)
        except HTTPException:
            await websocket.close(code=1008)
            return

        recipient = await user_service.get_user_with_profile(user_id_recipient)
        if not recipient:
            await websocket.close(code=1008)
            return

        room = await chat_service.get_and_create_room_by_users(user.id, user_id_recipient)
        room_id = room.id
        room_data = self.rooms.setdefault(room_id, {"connections": []})
        room_data["connections"].append(websocket)

        if room_id not in self.listener_tasks:
            self.listener_tasks[room_id] = asyncio.create_task(self.start_listener(room_id))

        cached_messages = await self.redis_utils.get_messages_list(room_id)

        if cached_messages:
            await websocket.send_json(list(reversed(cached_messages)))
            print("CACHED")
        else:
            print("NOT CACHED")
            messages = await chat_service.get_messages_for_room(room_id)
            message_list = [
                {
                    "text": message.text,
                    "user_id": message.user_id,
                    "avatarUrl": user.profile.avatar if message.user_id == user.id else recipient.profile.avatar
                }
                for message in messages
            ]
            await websocket.send_json(message_list)
            await self.redis_utils.add_message_to_list(room_id, message_list)

        return room_data["connections"], room, user, recipient

    async def send_message(
            self,
            data: dict,
            chat_service: ChatService,
            room_id: int,
            sender: User
    ) -> None:
        """
            Sends a message to all users in the room, adds the message to Redis,
            and broadcasts the data to all connected WebSocket clients.
        """
        message = await chat_service.add_message_to_room(room_id, {
            "text": data["text"],
            "user_id": sender.id
        })

        avatar_url = sender.profile.avatar
        data["avatarUrl"] = avatar_url

        await self.redis_utils.publish(
            f"chat:room:{room_id}:channel",
            {
                "text": message.text,
                "user_id": message.user_id,
                "avatarUrl": avatar_url
            }
        )
        try:
            if await self.redis_utils.message_list_exists(room_id):
                await self.redis_utils.add_message_to_list(room_id, {
                    "text": message.text,
                    "user_id": message.user_id,
                    "avatarUrl": avatar_url
                })
        except Exception:
            pass

    async def delete_room(self, room_id: int) -> None:
        """
            Deletes a room from the active room list.
        """
        if room_id in self.listener_tasks:
            task = self.listener_tasks[room_id]
            task.cancel()
            async with asyncio.TaskGroup() as tg:
                tg.create_task(task)
            del self.listener_tasks[room_id]

        if room_id in self.rooms:
            del self.rooms[room_id]


websocket_manager = WebsocketManager(redis_utils)

