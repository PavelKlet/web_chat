import uuid

from sqlalchemy import select

from infrastructure.repositories.base import SQLAlchemyRepository
from infrastructure.models.chat import Room


class RoomRepository(SQLAlchemyRepository):

    model = Room

    async def get_room_by_users(self, sender: int, recipient: int) -> Room:
        stmt = select(Room).filter(
            ((Room.sender_id == sender) & (Room.recipient_id == recipient)) |
            ((Room.sender_id == recipient) & (Room.recipient_id == sender))
        ).limit(1)

        result = await self.session.execute(stmt)
        room = result.scalar_one_or_none()

        if room is None:
            room_id = str(uuid.uuid4())
            new_room = Room(room_id=room_id, sender_id=sender,
                            recipient_id=recipient)
            self.session.add(new_room)
            await self.session.commit()
            return new_room

        return room
