from sqlalchemy import select
import uuid

from core.database import async_session_maker
from .models import Room, Message


async def get_room_by_users(sender: int, recipient: int):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(Room).filter(
                ((Room.sender_id == sender) & (Room.recipient_id == recipient)) |
                ((Room.sender_id == recipient) & (Room.recipient_id == sender))
            ).limit(1)

            result = await session.execute(stmt)
            room = result.scalar()

            if room is None:
                room_id = str(uuid.uuid4())
                new_room = Room(
                    room_id=room_id, sender_id=sender, recipient_id=recipient)
                session.add(new_room)
                room = new_room

        return room


async def get_messages_by_room_id(room_id: str):
    async with async_session_maker() as session:
        stmt = select(Message
                      ).filter(Message.room_id == room_id
                               ).order_by(Message.created_at.desc()).limit(10)
        result = await session.execute(stmt)
        messages = result.scalars().all()

    return messages


async def save_message(message: str, room_id: str):
    async with async_session_maker() as session:
        message = Message(text=message, room_id=room_id)
        session.add(message)
        await session.commit()


