import json
from typing import Sequence

from app.infrastructure.models.chat import Message, Room
from app.infrastructure.repositories.messages import MessageRepository
from app.infrastructure.repositories.room import RoomRepository
from app.application.unit_of_work.unit_of_work import UnitOfWork


class ChatService:
    """
       A service class for managing chat operations such as retrieving messages,
       adding new messages, and managing chat rooms.
    """

    def __init__(self, uow: UnitOfWork):
        """
            Initializes the ChatService with a UnitOfWork instance.
            Configures repositories for managing messages and chat rooms.
        """
        self.uow = uow
        self.uow.set_repository('message', MessageRepository)
        self.uow.set_repository('room', RoomRepository)

    async def get_messages_for_room(self, room_id: int) -> Sequence[Message]:
        """
            Retrieves all messages for a specific chat room.
        """
        async with self.uow:
            messages = await self.uow.message.get_messages_by_room_id(room_id)
            return messages

    async def add_message_to_room(self, room_id: int, data: dict):
        """
            Adds a new message to a chat room. If the room has more than 500 messages,
            deletes the oldest message.
        """
        async with self.uow:
            message_text = data.get("text")
            user_id = data.get("user_id")

            new_message_data = {
                "room_id": room_id,
                "text": message_text,
                "user_id": user_id
            }

            new_message = await self.uow.message.add_one(new_message_data)
            messages_count = await self.uow.message.get_messages_count(room_id)

            if messages_count > 500:
                oldest_message = await self.uow.message.get_oldest_message(room_id)
                if oldest_message:
                    await self.uow.message.delete(oldest_message)

            await self.uow.commit()

        return new_message

    async def delete_message(self, message_id: int):
        """
            Deletes a message by its ID.
        """
        async with self.uow:
            message = await self.uow.message.get_by_id(message_id)
            if message:
                await self.uow.message.delete(message)
                await self.uow.commit()

    async def get_room_by_users(self, sender: int, recipient: int) -> Room:
        """
            Retrieves a chat room that connects two users.
        """
        async with self.uow:
            room = await self.uow.room.get_room_by_users(sender, recipient)
            return room
