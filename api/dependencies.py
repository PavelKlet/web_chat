from typing import Annotated
from fastapi import Depends

from application.services.user import UserService
from application.unit_of_work.unit_of_work import UnitOfWork
from infrastructure.database import async_session_maker
from application.services.chat import ChatService

ChatServiceDep = Annotated[ChatService, Depends(lambda: ChatService(UnitOfWork(async_session_maker)))]
UserServiceDep = Annotated[UserService, Depends(lambda: UserService(UnitOfWork(async_session_maker)))]
