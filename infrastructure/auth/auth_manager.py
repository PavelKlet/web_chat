from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Depends

from infrastructure.config import settings
from application.services.user import UserService
from infrastructure.models.users import User
from api.dependencies import UserServiceDep


class AuthManager:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 1440
        self.ALGORITHM = "HS256"

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def get_user(
            self,
            request: Request = None,
            token: str = None,
    ) -> User | None:

        access_token = token if token else request.cookies.get("access_token")

        if not access_token:
            raise HTTPException(status_code=401, detail="Access token not found")

        try:
            payload = jwt.decode(
                access_token,
                settings.secret,
                algorithms=[self.ALGORITHM]
            )
            email = payload.get("sub")

            if not email:
                raise HTTPException(status_code=401, detail="Invalid token")

            user = await self.user_service.get_user_by_email(email)

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            return user

        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")


async def get_auth_manager(user_service: UserServiceDep) -> AuthManager:
    return AuthManager(user_service)


async def get_current_user(
    request: Request,
    auth_manager: AuthManager = Depends(get_auth_manager)
) -> User:
    token = request.cookies.get("access_token")
    return await auth_manager.get_user(request=request, token=token)
