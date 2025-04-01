from typing import Optional, Dict, Any, Sequence

from infrastructure.repositories.user import UserRepository
from application.unit_of_work.unit_of_work import UnitOfWork
from infrastructure.models.users import Profile, User


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.uow.set_repository('user', UserRepository)

    async def get_user_profile(self, user_id: int) -> Optional[Profile]:
        async with self.uow:
            profile = await self.uow.user.get_user_profile(user_id)
            return profile

    async def update_user_profile(self, user_id: int, update_data: Dict[str, Any]) -> None:
        async with self.uow:
            await self.uow.user.update_user_profile(user_id, update_data)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)
            return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self.uow:
            user = await self.uow.user.get_user_by_email(email)
            return user

    async def find_users_by_username(self, username_substring: str) -> Sequence[User]:
        async with self.uow:
            users = await self.uow.user.find_users_by_username(username_substring)
            return users

    async def get_user_friends(self, user_id: int, page: int, limit: int, paginated: bool) -> Sequence[User]:
        async with self.uow:
            friends = await self.uow.user.user_friends(user_id, page, limit, paginated)
            return friends

    async def add_user_friend(self, friend_id: int, user_id: int) -> None:
        async with self.uow:
            await self.uow.user.add_user_friend(friend_id, user_id)

    async def register_user(self, user_data: Dict[str, Any]) -> None:
        async with self.uow:
            await self.uow.user.user_register(user_data)

    async def check_user_in_friend(self, user_id: int, friend_id: int) -> bool:
        async with self.uow:
            is_friend = await self.uow.user.check_user_in_friend(user_id, friend_id)
            return is_friend

    async def get_user_friends_count(self, user_id: int) -> int:
        async with self.uow:
            count = await self.uow.user.get_user_friends_count(user_id)
            return count
