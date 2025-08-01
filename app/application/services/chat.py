from datetime import datetime
from typing import Sequence, List

from app.api.schemas.chat import RoomSchema, ChatItemSchema
from app.api.schemas.users import UserRead, FriendSchema
from app.infrastructure.models.nosql.messages import Message
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

    async def add_message_to_room(self, room_id: int, data: dict) -> Message:
        """
        Adds a new message to a chat room. If the room has more than 500 messages,
        deletes the oldest message.
        """
        message_text = data.get("text")
        user_id = data.get("user_id")
        username = data.get("username")

        new_message_data = {
            "room_id": room_id,
            "text": message_text,
            "user_id": user_id,
            "username": username
        }

        new_message = await self.message_repository.add_one(new_message_data)
        messages_count = await self.message_repository.get_messages_count(room_id)

        if messages_count > 500:
            oldest_message = await self.message_repository.get_oldest_message(room_id)
            if oldest_message:
                await self.message_repository.delete(oldest_message)
                await redis_utils.delete_all_messages(room_id)

        return new_message

    async def get_and_create_room_by_users(self, sender: int, recipient: int) -> RoomSchema:
        """
        Retrieves a chat room that connects two users.
        """
        async with self.uow:
            room = await self.uow.room.get_and_create_room_by_users(sender, recipient)
            return RoomSchema.model_validate(room)

    async def get_user_room_ids(self, user_id: int) -> list[tuple[int, int, int]]:
        """
        Returns a list of rooms in the format (room_id, sender_id, recipient_id).
        """
        async with self.uow:
            return await self.uow.room.get_user_room_ids(user_id)

    async def get_user_chat_list(
            self,
            user_id: int,
            rooms: list[tuple[int, int, int]],
            recipients: list[UserRead]
    ) -> List[ChatItemSchema]:

        recipients_map = {u.id: u for u in recipients}
        room_ids = [r[0] for r in rooms]
        last_messages = await self.message_repository.get_last_messages_for_rooms(room_ids)

        chat_list = []
        for room_id, sender_id, recipient_id in rooms:
            recipient_id = recipient_id if sender_id == user_id else sender_id
            recipient = recipients_map.get(recipient_id)
            msg = last_messages.get(room_id)

            if not msg:
                continue

            chat_list.append(ChatItemSchema(
                room_id=room_id,
                recipient=FriendSchema.model_validate(recipient),
                last_message=msg.text if msg else None,
                last_message_time=msg.created_at if msg else None,
            ))

        chat_list.sort(key=lambda chat: chat.last_message_time or datetime.min, reverse=True)

        return chat_list



