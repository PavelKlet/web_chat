import pytest
from sqlalchemy import select

from app.infrastructure.config.database import async_session_maker
from app.infrastructure.models.relational.users import Profile
from app.tests.fixtures.client import authorized_client

@pytest.mark.asyncio
async def test_get_profile_user(client):
    response = await client.get("/get/user-profile/1/")
    assert response.status_code == 200
    data = response.json()

    assert "username" in data
    assert "first_name" in data
    assert "last_name" in data
    assert "avatar" in data


@pytest.mark.asyncio
async def test_update_profile(authorized_client):
    data = {"first_name": "Updated", "last_name": "Name"}
    response = await authorized_client.post("/update-profile/", data=data)

    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"

    async with async_session_maker() as session:
        user = await session.execute(
            select(Profile).where(Profile.first_name == "Updated")
        )
        updated_profile = user.scalars().first()
        assert updated_profile is not None
        assert updated_profile.last_name == "Name"


@pytest.mark.asyncio
class TestLoginUser:


    async def test_login_user_success(self, client, create_user):


        login_data = {
            "email": create_user.email,
            "password": "test_password"
        }

        response = await client.post("/auth/jwt/login/", data=login_data)
        assert response.status_code == 200
        cookies = response.cookies
        assert "access_token" in cookies

        access_token = cookies["access_token"]
        assert access_token is not None

    async def test_login_user_invalid_password(self, client, create_user):

        login_data = {
            "email": create_user.email,
            "password": "wrong_password"
        }

        response = await client.post("/auth/jwt/login/", data=login_data)

        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect password"

    async def test_login_user_not_found(self, client):

        login_data = {
            "email": "nonexistent@example.com",
            "password": "test_password"
        }

        response = await client.post("/auth/jwt/login/", data=login_data)

        assert response.status_code == 400
        assert response.json()["detail"] == "User not found"
