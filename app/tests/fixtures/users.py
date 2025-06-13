import pytest_asyncio

from app.infrastructure.auth.auth_manager import AuthManager
from app.infrastructure.config.database import async_session_maker
from app.infrastructure.models.relational.users import User, Profile


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_user():
    auth_manager = AuthManager(user_service=None)

    password = "test_password"
    hashed_password = auth_manager.get_password_hash(password)

    async with async_session_maker() as session:
        user = User(
            email="testuser@example.com",
            username="testuser",
            hashed_password=hashed_password,
            profile=Profile(first_name="Test", last_name="User"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user