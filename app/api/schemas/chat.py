from pydantic import model_validator, BaseModel, EmailStr, ConfigDict

class RoomSchema(BaseModel):
    id: int
    room_id: str
    sender_id: int
    recipient_id: int

    class Config:
        from_attributes = True