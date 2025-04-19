import pytest_asyncio

from app.infrastructure.database import engine, Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_db():
    """Создаёт и удаляет таблицы перед каждым тестом."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)