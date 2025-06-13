import uuid

from sqlalchemy import select

from app.infrastructure.repositories.relational.base import SQLAlchemyRepository
from app.infrastructure.models.relational.rooms import Room


class RoomRepository(SQLAlchemyRepository):
    """
        Repository for managing Room entities in the database.

        This repository provides methods for fetching or creating a chat room
        between two users based on their IDs.
    """

    model = Room

    async def get_and_create_room_by_users(self, sender: int, recipient: int) -> Room:
        """
            Retrieves an existing chat room between two users or creates a new one
            if no room exists.
        """

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
