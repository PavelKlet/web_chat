import pytest_asyncio
from httpx import AsyncClient

from app.application.services.auth.auth_manager import AuthManager
from app.main import app


@pytest_asyncio.fixture(scope="function")
async def authorized_client(create_user):
    auth_manager = AuthManager(None)
    token = auth_manager.create_access_token({"sub": create_user.email})

    client = AsyncClient(app=app, base_url="http://testserver")
    client.cookies.set("access_token", token)
    yield client
    await client.aclose()

@pytest_asyncio.fixture(scope="function")
async def client():
    client = AsyncClient(app=app, base_url="http://testserver")
    yield client
    await client.aclose()