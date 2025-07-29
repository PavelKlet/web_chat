from datetime import datetime
from typing import Optional

from pydantic import model_validator, BaseModel, EmailStr, ConfigDict

from app.api.schemas.users import FriendSchema


class RoomSchema(BaseModel):
    id: int
    room_id: str
    sender_id: int
    recipient_id: int

    class Config:
        from_attributes = True

class ChatListItemSchema(BaseModel):
    room_id: int
    recipient: FriendSchema
    last_message: Optional[str]
    last_message_time: Optional[datetime]

    class Config:
        from_attributes = True