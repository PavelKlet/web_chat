from typing import Sequence

from sqlalchemy import select, func
from app.infrastructure.models.chat import Message
from .base import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository):
    """
        Repository for managing Message entities in the database.

        This repository provides specialized methods for working with messages,
        including fetching messages for a specific room, counting messages, and
        retrieving the oldest message in a room.
    """

    model = Message

    async def get_messages_by_room_id(self, room_id: int) -> Sequence[Message]:
        """
            Retrieves all messages associated with a specific room ID.
        """
        stmt = select(Message).where(Message.room_id == room_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_messages_count(self, room_id: int) -> int:
        """
            Counts the number of messages in a specific room.
        """
        stmt = select(func.count()).where(Message.room_id == room_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_oldest_message(self, room_id: int) -> Message:
        """
            Retrieves the oldest message in a specific room.
        """
        stmt = select(Message).where(Message.room_id == room_id).order_by(Message.created_at).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()