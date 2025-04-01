import json
from typing import Tuple, List, Optional

from fastapi import WebSocket
from fastapi.exception_handlers import HTTPException

from users.auth import auth_manager
from users.crud import RepositoryUser
from users.models import User
from .crud import get_room_by_users, get_messages_by_room_id
from .models import Room


class WebsocketManager(object):

    def __init__(self):
        self.rooms = {}

    async def connect(
            self,
            websocket: WebSocket,
            user_id_recipient: int,
            session: RepositoryUser
    ) -> Optional[Tuple[List[WebSocket], Room, User, User]]:

        await websocket.accept()

        access_token = await websocket.receive_text()

        try:
            user = await auth_manager.get_user(
                token=access_token, session=session)
        except HTTPException:
            await websocket.close()
            return

        recipient = await session.get_user_by_id(user_id_recipient)

        if not recipient:
            await websocket.close()
            return

        room = await get_room_by_users(user.id, user_id_recipient)

        if room.id in self.rooms.keys():
            room_connections = self.rooms[room.id]
        else:
            room_connections = []
            self.rooms[room.id] = room_connections

        room_connections.append(websocket)

        messages = await get_messages_by_room_id(room.id)
        for message in messages[::-1]:
            await websocket.send_json(json.loads(message.text))

        return room_connections, room, user, recipient

    async def send_message(
            self,
            room_connections: List[WebSocket],
            data: str
    ) -> None:

        for connection in room_connections:
            await connection.send_json(data)

    async def delete_room(self, room_id: int):
        del self.rooms[room_id]


websocket_manager = WebsocketManager()
