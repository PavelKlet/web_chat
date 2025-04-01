# from jose import jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from fastapi import HTTPException, Request, Depends
#
# from .crud import RepositoryUser, session_dependency
# from core.config import settings
# from .models import User
#
#
# class AuthManager:
#     def __init__(self):
#         self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#         self.ACCESS_TOKEN_EXPIRE_MINUTES = 1440
#         self.ALGORITHM = "HS256"
#
#     def verify_password(self, plain_password, hashed_password):
#         return self.pwd_context.verify(plain_password, hashed_password)
#
#     def get_password_hash(self, password):
#         return self.pwd_context.hash(password)
#
#     def create_access_token(self, data: dict):
#         to_encode = data.copy()
#         expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
#         to_encode.update({"exp": expire})
#         encoded_jwt = jwt.encode(to_encode, settings.secret, algorithm=self.ALGORITHM)
#         return encoded_jwt
#
#     async def get_user(
#             self,
#             request: Request = None,
#             token: str = None,
#             session: RepositoryUser = Depends(session_dependency.get_session)
#     ) -> User | None:
#
#         access_token = token
#         if not token:
#             access_token = request.cookies.get("access_token")
#
#         if not access_token:
#             raise HTTPException(status_code=401, detail="Access token not found")
#
#         try:
#             payload = jwt.decode(
#                 access_token,
#                 settings.secret,
#                 algorithms=[self.ALGORITHM]
#             )
#             email = payload.get("sub")
#
#             if not email:
#                 raise HTTPException(status_code=401, detail="Invalid token")
#
#             user = await session.get_user_by_email(email)
#
#             if not user:
#                 raise HTTPException(status_code=404, detail="User not found")
#
#             return user
#
#         except jwt.JWTError:
#             raise HTTPException(status_code=401, detail="Invalid token")
#
#
# auth_manager = AuthManager()
