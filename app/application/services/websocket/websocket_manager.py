from typing import Tuple, List, Optional

from fastapi import WebSocket, HTTPException

from app.api.schemas.users import UserRead
from app.application.services.auth.auth_manager import AuthManager
from app.infrastructure.models.relational.rooms import Room
from app.application.services.chat import ChatService
from app.application.services.user import UserService
from app.infrastructure.utils.redis_utils.redis_utils import RedisUtils, redis_utils

class WebsocketManager:
    """
        A class responsible for managing WebSocket connections, handling connections,
        sending messages in the chat, and caching messages in Redis.
    """

    def __init__(self, redis: RedisUtils):
        self.redis_utils = redis
        self.rooms: dict[int, dict[str, list[WebSocket]]] = {}
        self.chat_listeners: list[WebSocket] = []

    async def connect_chat_list(
            self,
            websocket: WebSocket,
            auth_manager: AuthManager
    ):
        """Connecting to the chat list page."""
        await websocket.accept()

        try:
            access_token = await websocket.receive_text()
            user = await auth_manager.get_user(token=access_token)
        except HTTPException:
            await websocket.close(code=1008)
            return

        self.chat_listeners.append(websocket)
        return user

    async def broadcast_to_room(self, room_id: int, payload: dict):
        """Sending a message to everyone in the room"""
        connections = self.rooms.get(room_id, {}).get("connections", [])
        if not connections:
            await self.delete_room(room_id)
            return

        dead = []
        for ws in connections:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            connections.remove(ws)

        if not connections:
            await self.delete_room(room_id)

    async def broadcast_chat_update(self, payload: dict):
        """Sending chat list updates"""
        dead = []
        for ws in self.chat_listeners:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.chat_listeners.remove(ws)


    async def connect(
            self,
            websocket: WebSocket,
            user_id_recipient: int,
            chat_service: ChatService,
            user_service: UserService,
            auth_manager: AuthManager
    ) -> Optional[Tuple[List[WebSocket], Room, UserRead, UserRead]]:

        """
            Establishes a WebSocket connection, authenticates the user with a token,
            finds or creates a chat room, and sends the message history from Redis or a database using Redis pub/sub.
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

        try:
            cached_messages = await self.redis_utils.get_messages_list(room_id)
        except Exception:
            cached_messages = None

        if cached_messages:
            await websocket.send_json(list(reversed(cached_messages)))
        else:
            messages = await chat_service.get_messages_for_room(room_id)
            message_list = [
                {   "username": message.username,
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
            sender: UserRead
    ) -> None:
        """
            Sends a message to all users in the room, adds the message to Redis,
            and broadcasts the data to all connected WebSocket clients.
        """
        message = await chat_service.add_message_to_room(room_id, {
            "username": data["username"],
            "text": data["text"],
            "user_id": sender.id
        })

        avatar_url = sender.profile.avatar

        message_data = {
            "username": message.username,
            "text": message.text,
            "user_id": message.user_id,
            "avatarUrl": avatar_url,
            "type": "chat_message"
        }

        update_event = {
            "room_id": room_id,
            "last_message": message.text,
            "sender_id": sender.id,
            "type": "chat_update"
        }

        await self.redis_utils.publish(
            f"chat:room:{room_id}:channel",
            message_data
        )
        await self.redis_utils.publish(
            f"chat:room:{room_id}:channel",
            update_event
        )

        del message_data["type"]
        try:
            if await self.redis_utils.message_list_exists(room_id):
                await self.redis_utils.add_message_to_list(room_id, message_data)
        except Exception:
            pass

    async def delete_room(self, room_id: int) -> None:
        """
            Deletes a room from the active room list and cancel pub/sub task.
        """

        if room_id in self.rooms:
            del self.rooms[room_id]


websocket_manager = WebsocketManager(redis_utils)

