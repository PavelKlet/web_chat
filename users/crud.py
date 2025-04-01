# from pathlib import Path
# from typing import Optional, Any, Sequence, List
# import os
#
# from sqlalchemy import select, insert
# from sqlalchemy.engine import Result
# from sqlalchemy.orm import selectinload
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.sql.expression import func
# from sqlalchemy.engine.result import Row, RowMapping
# from fastapi import UploadFile, HTTPException
# from urllib.parse import urlparse
# from aiofiles import open
#
# from core.database import async_session_maker, SessionDependency
# # from .models import Profile, User,friends
# from redis_utils.redis_utils import redis_utils
#
#
# class UserSessionDependency(SessionDependency):
#
#     async def get_session(self):
#         async with self.sessionmaker() as session:
#             yield RepositoryUser(session)
#
#
# async def save_and_get_avatar_path(avatar: UploadFile, user_id: int) -> str:
#     filename = os.path.basename(urlparse(avatar.filename).path)
#     filename_without_extension = Path(filename).stem
#     file_extension = Path(filename).suffix
#     user_directory = f"media/{user_id}"
#
#     os.makedirs(user_directory, exist_ok=True)
#     file_list = os.listdir(user_directory)
#
#     if file_list:
#         for file_name in file_list:
#             file_path = os.path.join(user_directory, file_name)
#             os.remove(file_path)
#
#     new_filename = f"{filename_without_extension}{file_extension}"
#     upload_path = f"{user_directory}/{new_filename}"
#
#     async with open(upload_path, "wb") as file:
#         content = await avatar.read()
#         await file.write(content)
#
#     return "/" + upload_path
#
#
# class RepositoryUser:
#     def __init__(self, session: AsyncSession):
#         self.session = session
#
#     async def get_user_profile(self, user_id: int) -> Profile | None:
#         stmt = select(Profile).where(Profile.user_id == user_id)
#         result: Result = await self.session.execute(stmt)
#         profile: Profile | None = result.scalar_one_or_none()
#         return profile
#
#     async def update_user_profile(
#         self,
#         user_id: Optional[int],
#         first_name: Optional[str],
#         last_name: Optional[str],
#         avatar: Optional[UploadFile] = None,
#     ) -> None:
#
#         try:
#             profile = await self.get_user_profile(user_id)
#
#             if not profile:
#                 raise HTTPException(status_code=404,
#                                     detail="Профиль пользователя не найден")
#             if first_name:
#                 profile.first_name = first_name
#             if last_name:
#                 profile.last_name = last_name
#             if avatar and avatar.content_type.startswith("image"):
#                 try:
#                     upload_path = await save_and_get_avatar_path(avatar,
#                                                                  user_id)
#                     profile.avatar = upload_path
#                 except IOError:
#                     raise HTTPException(status_code=400,
#                                         detail="Ошибка обработки изображения")
#
#             self.session.add(profile)
#             await self.session.commit()
#         except Exception as e:
#             await self.session.rollback()
#             raise e
#
#     async def get_user_by_id(self, user_id: int) -> User | None:
#         stmt = select(User).where(User.id == user_id)
#         result: Result = await self.session.execute(stmt)
#         user: User | None = result.scalar_one_or_none()
#         return user
#
#     async def get_user_friends_count(self, user: User):
#         cache_key = f"user_friends_count:{user.id}"
#         cached_data = await redis_utils.get(cache_key)
#
#         if cached_data:
#             friends_count = int(cached_data)
#         else:
#             stmt = select(
#                 func.count()
#             ).select_from(friends).filter(friends.c.user_id == user.id)
#             result = await self.session.execute(stmt)
#             friends_count = result.scalar()
#             await redis_utils.set(cache_key, friends_count, expire=3600)
#         return friends_count
#
#     async def user_friends(
#             self,
#             user: User, page: int, limit: int, paginated: bool
#     ) -> Sequence[Row | RowMapping | Any]:
#
#         stmt = select(User).join(
#             friends,
#             User.id == friends.c.friend_id
#         ).filter(
#             friends.c.user_id == user.id
#         )
#
#         if paginated:
#             stmt = stmt.order_by(User.id)
#         else:
#             limit = 3
#             stmt = stmt.order_by(func.random())
#
#         stmt = stmt.options(
#             selectinload(User.profile))
#         stmt = stmt.offset((page - 1) * limit).limit(limit)
#         result = await self.session.execute(stmt)
#         friends_user = result.scalars().all()
#         return friends_user
#
#     async def add_user_friend(self, friend_id: int, user: User) -> None:
#         try:
#             friend = await self.get_user_by_id(friend_id)
#             if friend:
#                 await self.session.execute(insert(friends).values(
#                     user_id=user.id,
#                     friend_id=friend.id
#                 ))
#             await self.session.commit()
#         except Exception as e:
#             await self.session.rollback()
#             raise e
#
#     async def user_register(
#             self,
#             email: str,
#             hashed_password: str,
#             username: str
#     ) -> None:
#         try:
#             new_user = User(email=email, hashed_password=hashed_password,
#                             username=username)
#             new_profile = Profile(avatar="/media/default/default.webp")
#             new_user.profile = new_profile
#             self.session.add(new_user)
#             await self.session.commit()
#         except Exception as e:
#             await self.session.rollback()
#             raise e
#
#     async def get_user_by_email(self, email: str) -> User | None:
#         stmt = select(User).where(User.email == email
#                                   ).options(selectinload(User.profile))
#         result: Result = await self.session.execute(stmt)
#         user: User | None = result.scalar_one_or_none()
#         return user
#
#     async def find_users_by_username(self, username_substring
#                                      ) -> Sequence[Row | RowMapping | Any]:
#         stmt = select(User).where(
#             User.username.contains(username_substring)).options(
#             selectinload(User.profile))
#
#         result = await self.session.execute(stmt)
#         users = result.scalars().all()
#
#         return users
#
#     async def check_user_in_friend(self, user_id: int, friend_id: int) -> bool:
#         query = select(friends).where(
#             (friends.c.user_id == user_id) & (friends.c.friend_id == friend_id)
#         )
#         result = await self.session.execute(query)
#         return result.scalar() is not None
#
#
# session_dependency = UserSessionDependency(async_session_maker)
#
#
