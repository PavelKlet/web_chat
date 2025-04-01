from typing import Sequence

from sqlalchemy import select
from infrastructure.models.chat import Message
from .base import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository):

    model = Message

    async def get_messages_by_room_id(self, room_id: int) -> Sequence[Message]:
        stmt = select(Message).where(Message.room_id == room_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
