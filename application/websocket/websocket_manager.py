import json
from typing import Tuple, List, Optional

from fastapi import WebSocket, HTTPException

from infrastructure.auth.auth_manager import AuthManager
from infrastructure.models.chat import Room
from application.services.chat import ChatService
from application.services.user import UserService
# from users.models import User
from infrastructure.models.users import User


class WebsocketManager:
    def __init__(self):
        self.rooms = {}

    async def connect(
            self,
            websocket: WebSocket,
            user_id_recipient: int,
            chat_service: ChatService,
            user_service: UserService,
            auth_manager: AuthManager
    ) -> Optional[Tuple[List[WebSocket], Room, User, User]]:

        await websocket.accept()

        access_token = await websocket.receive_text()

        try:
            user = await auth_manager.get_user(token=access_token)
        except HTTPException:
            await websocket.close()
            return

        recipient = await user_service.get_user_by_id(user_id_recipient)
        if not recipient:
            await websocket.close()
            return

        room = await chat_service.get_room_by_users(user.id, user_id_recipient)
        if room.id in self.rooms:
            room_connections = self.rooms[room.id]
        else:
            room_connections = []
            self.rooms[room.id] = room_connections

        room_connections.append(websocket)

        messages = await chat_service.get_messages_for_room(room.id)
        for message in messages:
            await websocket.send_json(json.loads(message.text))

        return room_connections, room, user, recipient

    async def send_message(
            self,
            room_connections: List[WebSocket],
            data: dict,
            chat_service: ChatService,
            room_id: int
    ) -> None:

        await chat_service.add_message_to_room(room_id, data)

        for connection in room_connections:
            await connection.send_json(data)

    async def delete_room(self, room_id: str) -> None:
        if room_id in self.rooms:
            del self.rooms[room_id]


websocket_manager = WebsocketManager()

