from pydantic import model_validator, BaseModel, EmailStr
from typing import Optional
import re


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def validate_password(self):
        pw1 = self.password
        pw2 = self.confirm_password
        if len(pw1) < 8:
            raise ValueError("Пароль должен содержать как минимум 8 символов")
        if len(re.findall(r"\d", pw1)) < 2:
            raise ValueError("Пароль должен содержать как минимум 2 цифры")
        if pw1 != pw2:
            raise ValueError("Пароли не совпадают")
        del self.confirm_password
        return self


class FriendData(BaseModel):
    id: int
    avatar: Optional[str]
    username: str
    first_name: Optional[str]
    last_name: Optional[str]


class UserProfileData(BaseModel):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]


class UserData(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    user_id: int
    username: str
