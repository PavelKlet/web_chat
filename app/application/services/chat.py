from typing import Sequence

from sqlalchemy.orm import Mapped

from app.infrastructure.models.nosql.messages import Message
from app.infrastructure.models.relational.rooms import Room
from app.infrastructure.repositories.nosql.messages import MessageRepositoryMongoDB
from app.infrastructure.repositories.relational.room import RoomRepository
from app.application.unit_of_work.unit_of_work import IUnitOfWork
from app.infrastructure.utils.redis_utils.redis_utils import redis_utils


class ChatService:
    """
    A service class for managing chat operations such as retrieving messages,
    adding new messages, and managing chat rooms.
    """

    def __init__(self, uow: IUnitOfWork):
        """
        Initializes the ChatService with a UnitOfWork instance and a MongoDB repository.
        Configures repositories for managing messages and chat rooms.
        """
        self.uow = uow
        self.message_repository = MessageRepositoryMongoDB()
        self.uow.set_repository('room', RoomRepository)

    async def get_messages_for_room(self, room_id: int) -> Sequence[Message]:
        """
        Retrieves all messages for a specific chat room.
        """
        return await self.message_repository.get_messages_by_room_id(room_id)

    async def add_message_to_room(self, room_id: int, data: dict):
        """
        Adds a new message to a chat room. If the room has more than 500 messages,
        deletes the oldest message.
        """
        message_text = data.get("text")
        user_id = data.get("user_id")

        new_message_data = {
            "room_id": room_id,
            "text": message_text,
            "user_id": user_id
        }

        new_message = await self.message_repository.add_one(new_message_data)
        messages_count = await self.message_repository.get_messages_count(room_id)

        if messages_count > 500:
            oldest_message = await self.message_repository.get_oldest_message(room_id)
            if oldest_message:
                await self.message_repository.delete(oldest_message)
                await redis_utils.delete_all_messages(room_id)

        return new_message

    async def delete_message(self, message_id: int):
        """
        Deletes a message by its ID.
        """
        message = await self.message_repository.get_by_id(message_id)
        if message:
            await self.message_repository.delete(message)

    async def get_and_create_room_by_users(self, sender: Mapped[int], recipient: int) -> Room:
        """
        Retrieves a chat room that connects two users.
        """
        async with self.uow:
            room = await self.uow.room.get_and_create_room_by_users(sender, recipient)
            return room
