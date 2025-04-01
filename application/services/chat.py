import json
from typing import Sequence

from infrastructure.models.chat import Message, Room
from infrastructure.repositories.messages import MessageRepository
from infrastructure.repositories.room import RoomRepository
from application.unit_of_work.unit_of_work import UnitOfWork


class ChatService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.uow.set_repository('message', MessageRepository)
        self.uow.set_repository('room', RoomRepository)

    async def get_messages_for_room(self, room_id: int) -> Sequence[Message]:
        async with self.uow:
            messages = await self.uow.message.get_messages_by_room_id(room_id)
            return messages

    async def add_message_to_room(self, room_id: int, data: dict):
        async with self.uow:
            message_data = json.dumps(data)
            new_message_data = {
                "room_id": room_id,
                "text": message_data,
            }
            await self.uow.message.add_one(new_message_data)
            await self.uow.commit()

    async def delete_message(self, message_id: int):
        async with self.uow:
            message = await self.uow.message.get_by_id(message_id)
            if message:
                await self.uow.message.delete(message)
                await self.uow.commit()

    async def get_room_by_users(self, sender: int, recipient: int) -> Room:
        async with self.uow:
            room = await self.uow.room.get_room_by_users(sender, recipient)
            return room
