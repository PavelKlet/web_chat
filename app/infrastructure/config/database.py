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
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.infrastructure.models.nosql.messages import Message
from app.infrastructure.config.config import settings


class MongoDB:
    def __init__(self, mongo_uri: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]

    async def init_models(self):
        """
        Initialization of models to work with Beanie.
        """
        await init_beanie(database=self.db, document_models=[Message])

class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)


mongo_db = MongoDB(mongo_uri=settings.mongo_uri, db_name=settings.mongo_db_name)

async def init_mongo():
    await mongo_db.init_models()

engine = create_async_engine(
    settings.postgresql_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
