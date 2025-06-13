class BaseMongoRepository:
    model = None

    async def add_one(self, data: dict):
        obj = self.model(**data)
        await obj.insert()
        return obj

    @staticmethod
    async def delete(obj):
        await obj.delete()
