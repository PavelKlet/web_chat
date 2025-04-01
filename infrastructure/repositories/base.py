from typing import Optional, TypeVar, Dict, Type
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyRepository:

    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, item_id: int) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == item_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add_one(self, data: Dict) -> Optional[ModelType]:
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, obj: ModelType, updated_data: Dict) -> Optional[ModelType]:
        for key, value in updated_data.items():
            setattr(obj, key, value)
        await self.session.commit()
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)
        await self.session.commit()
