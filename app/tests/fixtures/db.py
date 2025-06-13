import pytest_asyncio

from app.infrastructure.config.database import engine, Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)