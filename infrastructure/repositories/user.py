from typing import Optional, Dict, Any, Sequence
from sqlalchemy.future import select
from sqlalchemy import insert, func
from sqlalchemy.orm import selectinload
from infrastructure.models.users import User, Profile, friends
from starlette.datastructures import UploadFile
from fastapi import HTTPException

from infrastructure.utils.redis_utils.redis_utils import redis_utils
from .base import SQLAlchemyRepository
from infrastructure.utils.file_utils import save_and_get_avatar_path


class UserRepository(SQLAlchemyRepository):

    model = User

    async def get_user_profile(self, user_id: int) -> Optional[Profile]:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_profile(self, user_id: int, update_data: Dict[str, Any]) -> None:
        try:
            profile = await self.get_user_profile(user_id)

            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")

            for key, value in update_data.items():
                if key == "avatar" and value:
                    if isinstance(value, UploadFile) and value.content_type.startswith("image"):
                        try:
                            upload_path = await save_and_get_avatar_path(value, user_id)
                            profile.avatar = upload_path
                        except IOError:
                            raise HTTPException(status_code=400, detail="Error processing image")
                else:
                    setattr(profile, key, value)

            self.session.add(profile)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email).options(selectinload(User.profile))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_users_by_username(self, username_substring: str) -> Sequence[User]:
        stmt = select(User).where(User.username.contains(username_substring)).options(selectinload(User.profile))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def user_friends(self, user_id: int, page: int, limit: int, paginated: bool) -> Sequence[User]:
        stmt = select(User).join(
            friends, User.id == friends.c.friend_id
        ).filter(
            friends.c.user_id == user_id
        )

        if paginated:
            stmt = stmt.order_by(User.id)
        else:
            limit = 3
            stmt = stmt.order_by(func.random())

        stmt = stmt.options(selectinload(User.profile))
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_user_friend(self, friend_id: int, user_id: int) -> None:
        try:
            friend = await self.get_by_id(friend_id)
            if friend:
                await self.session.execute(insert(friends).values(
                    user_id=user_id,
                    friend_id=friend.id
                ))
                await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def user_register(self, user_data: Dict[str, Any]) -> None:
        try:
            new_user = User(**user_data)
            new_profile = Profile(avatar="/media/default/default.png")
            new_user.profile = new_profile
            self.session.add(new_user)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def check_user_in_friend(self, user_id: int, friend_id: int) -> bool:
        query = select(friends).where(
            (friends.c.user_id == user_id) & (friends.c.friend_id == friend_id)
        )
        result = await self.session.execute(query)
        return result.scalar() is not None

    async def get_user_friends_count(self, user: User) -> int:
        cache_key = f"user_friends_count:{user.id}"
        cached_data = await redis_utils.get(cache_key)

        if cached_data:
            friends_count = int(cached_data)
        else:
            stmt = select(
                func.count()
            ).select_from(friends).filter(friends.c.user_id == user.id)
            result = await self.session.execute(stmt)
            friends_count = result.scalar()
            await redis_utils.set(cache_key, friends_count, expire=3600)
        return friends_count
