from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Depends
from ..config import settings
from app.application.services.user import UserService
from ..models.users import User
from app.api.dependencies import UserServiceDep


class AuthManager:
    """
        Manages authentication-related operations such as password hashing, token creation,
        and user verification via access tokens.
    """

    def __init__(self, user_service: UserService):
        """
            Initializes the AuthManager with the user service for user lookup and a password context for password hashing.
        """
        self.user_service = user_service
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 1440
        self.ALGORITHM = "HS256"

    def verify_password(self, plain_password, hashed_password):
        """
           Verifies that the provided plain password matches the hashed password.
       """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        """
            Hashes the provided password using bcrypt.
        """
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict):
        """
            Creates an access token with the specified data, including an expiration time.
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def get_user(
            self,
            request: Request = None,
            token: str = None,
    ) -> User | None:
        """
            Retrieves the user associated with the provided access token. If the token is not provided, it checks the cookies.
        """
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
    """
        Provides an instance of the AuthManager for handling authentication tasks.
    """

    return AuthManager(user_service)


async def get_current_user(
    request: Request,
    auth_manager: AuthManager = Depends(get_auth_manager)
) -> User:
    """
        Retrieves the currently authenticated user by extracting the access token from the request cookies.
    """
    token = request.cookies.get("access_token")
    return await auth_manager.get_user(request=request, token=token)
