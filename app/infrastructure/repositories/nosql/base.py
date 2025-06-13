class BaseMongoRepository:
    model = None

    async def add_one(self, data: dict):
        obj = self.model(**data)
        await obj.insert()
        return obj

    async def get_by_id(self, id: str):
        return await self.model.find_one(self.model.id == id)

    @staticmethod
    async def delete(obj):
        await obj.delete()
