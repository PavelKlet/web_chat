from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
)
from abc import ABC, abstractmethod
from infrastructure.config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)


engine = create_async_engine(settings.postgresql_url)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class SessionDependency(ABC):
    def __init__(self, sessionmaker: async_session_maker):
        self.sessionmaker = sessionmaker

    @abstractmethod
    async def get_session(self):
        raise NotImplementedError
