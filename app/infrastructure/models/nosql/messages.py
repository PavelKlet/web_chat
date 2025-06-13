from datetime import datetime
from beanie import Document
from pydantic import Field

class Message(Document):
    room_id: int = Field(..., description="ID комнаты")
    user_id: int = Field(..., description="ID пользователя")
    text: str = Field(..., max_length=1024, description="Текст сообщения")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания")

    class Settings:
        name = "messages"
        indexes = [
            "room_id",
            [("room_id", 1), ("created_at", 1)],
        ]
