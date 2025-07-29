from typing import Optional, Dict, Any, Sequence

from app.infrastructure.repositories.relational.user import UserRepository
from app.application.unit_of_work.unit_of_work import UnitOfWork
from ..exceptions import EmailAlreadyExistsException, UsernameAlreadyExistsException
from app.api.schemas.users import UserRead, FriendSchema, UserReadPrivate


class UserService:
    """
        A service class for managing user operations such as retrieving and updating profiles,
        finding friends, and handling user registration and login.
    """

    def __init__(self, uow: UnitOfWork):
        """
            Initializes the UserService with a UnitOfWork instance.
            Configures the user repository for interacting with user data.
        """
        self.uow = uow
        self.uow.set_repository('user', UserRepository)

    async def get_user_with_profile(self, user_id: int) -> Optional[UserRead]:
        """
            Retrieves a user along with their profile information.
        """
        async with self.uow:
            user = await self.uow.user.get_user_with_profile(user_id)
            return UserRead.model_validate(user)

    async def get_user_profile(self, user_id: int) -> Optional[UserRead]:
        """
            Retrieves the profile information for a specific user.
        """
        async with self.uow:
            profile = await self.uow.user.get_user_profile(user_id)
            return UserRead.model_validate(profile)

    async def update_user_profile(self, user_id: int, update_data: Dict[str, Any]) -> None:
        """
            Updates a user's profile with the provided data.
        """
        async with self.uow:
            await self.uow.user.update_user_profile(user_id, update_data)

    async def get_user_by_id(self, user_id: int) -> Optional[UserRead]:
        """
            Retrieves a user by their ID.
        """
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)
            return UserRead.model_validate(user)

    async def get_user_by_email(self, email: str) -> Optional[UserRead]:
        """
           Retrieves a user by their email.
       """
        async with self.uow:
            user = await self.uow.user.get_user_by_email(email)
            return UserRead.model_validate(user)

    async def get_user_by_email_private(self, email: str) -> Optional[UserReadPrivate]:
        async with self.uow:
            user = await self.uow.user.get_user_by_email(email)
            if user:
                return UserReadPrivate.model_validate(user)
            return None

    async def find_users_by_username(self, username_substring: str, page: int, limit: int) -> Sequence[FriendSchema]:
        """
            Finds users by a partial username.
        """
        async with self.uow:
            users = await self.uow.user.find_users_by_username(username_substring, page, limit)
            return [FriendSchema.model_validate(user) for user in users]

    async def get_user_friends(self, user_id: int, page: int, limit: int, paginated: bool) -> Sequence[FriendSchema]:
        """
           Retrieves a user's friends.
       """
        async with self.uow:
            friends = await self.uow.user.user_friends(user_id, page, limit, paginated)
            return [FriendSchema.model_validate(friend) for friend in friends]


    async def add_user_friend(self, friend_id: int, user_id: int) -> None:
        """
            Adds a user to the current user's friend list.
        """
        async with self.uow:
            await self.uow.user.add_user_friend(friend_id, user_id)

    async def register_user(self, user_data: Dict[str, Any]) -> None:
        """
            Registers a new user with the provided data.
        """
        async with self.uow:

            existing_email_user = await self.uow.user.get_user_by_email(user_data["email"])
            if existing_email_user:
                raise EmailAlreadyExistsException("Email already exists")

            existing_username_user = await self.uow.user.get_user_by_username(user_data["username"])
            if existing_username_user:
                raise UsernameAlreadyExistsException("Username already exists")

            await self.uow.user.user_register(user_data)

    async def check_user_in_friend(self, user_id: int, friend_id: int) -> bool:
        """
            Checks if a user is a friend of another user.
        """
        async with self.uow:
            is_friend = await self.uow.user.check_user_in_friend(user_id, friend_id)
            return is_friend

    async def get_user_friends_count(self, user_id: int) -> int:
        """
            Retrieves the count of a user's friends.
        """
        async with self.uow:
            count = await self.uow.user.get_user_friends_count(user_id)
            return count

    async def get_users_with_profiles(self, user_ids: list[int]) -> list[UserRead]:
        async with self.uow:
            users = await self.uow.user.get_users_with_profiles(user_ids)
            return [UserRead.model_validate(user) for user in users]

