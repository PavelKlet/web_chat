from typing import Optional, TypeVar, Dict
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyRepository:
    """
    A generic repository for handling common database operations using SQLAlchemy.

    Attributes:
        model (Base): The SQLAlchemy model class associated with this repository.
        session (AsyncSession): The SQLAlchemy asynchronous session used for database interactions.

    Methods:
        get_by_id(item_id: int): Retrieves an instance of the model by its ID.
        add_one(data: Dict): Inserts a new record into the database with the provided data.
        update(obj: ModelType, updated_data: Dict): Updates an existing record with new data.
        delete(obj: ModelType): Deletes the specified record from the database.
    """

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
