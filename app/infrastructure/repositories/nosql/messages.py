from typing import List

from app.infrastructure.models.nosql.messages import Message
from app.infrastructure.repositories.nosql.base import BaseMongoRepository


class MessageRepositoryMongoDB(BaseMongoRepository):
    model = Message

    async def get_messages_by_room_id(self, room_id: int, limit: int = 500) -> List[Message]:
        return await self.model.find(self.model.room_id == room_id).sort("+created_at").limit(limit).to_list()

    async def get_messages_count(self, room_id: int) -> int:
        return await self.model.find(self.model.room_id == room_id).count()

    async def get_oldest_message(self, room_id: int) -> Message:
        return await self.model.find(self.model.room_id == room_id).sort("+created_at").first_or_none()

    async def delete_oldest_message(self, room_id: int) -> None:
        oldest_message = await self.get_oldest_message(room_id)
        if oldest_message:
            await oldest_message.delete()

    async def get_last_messages_for_rooms(self, room_ids: list[int]) -> dict[int, Message]:
        pipeline = [
            {"$match": {"room_id": {"$in": room_ids}}},
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": "$room_id",
                "doc": {"$first": "$$ROOT"}
            }},
        ]
        cursor = self.model.get_motor_collection().aggregate(pipeline)
        results = await cursor.to_list(length=len(room_ids))

        return {
            r["_id"]: self.model.model_validate(r["doc"])
            for r in results
        }
