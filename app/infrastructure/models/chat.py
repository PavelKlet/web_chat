from datetime import datetime

from app.infrastructure.database import Base
from sqlalchemy import (
    String,
    ForeignKey,
    BIGINT,
    UniqueConstraint,
    JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Message(Base):
    """
   Represents a message in a chat room.
   Attributes:
       text (str): The content of the message.
       created_at (datetime): The timestamp when the message was created. Defaults to the current time.
       room_id (int): The ID of the chat room this message belongs to.
       user_id (int): The ID of the user who sent the message.
   """
    text = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    room_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('room.id'))
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('user.id'))


class Room(Base):
    """
    Represents a chat room.
    Attributes:
        room_id (str): A unique identifier for the room.
        sender_id (int): The ID of the user who initiated the chat.
        recipient_id (int): The ID of the user who is the recipient of the chat.
        messages (List[Message]): A list of messages exchanged in the room.
        sender (User): The user who initiated the chat (foreign key to the User table).
        recipient (User): The recipient of the chat (foreign key to the User table).
    Constraints:
        UniqueConstraint: Ensures that there can only be one chat room for a specific sender-recipient pair.
    """
    room_id: Mapped[str] = mapped_column(String(length=250))
    sender_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('user.id'))
    recipient_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('user.id'))
    messages = relationship("Message")
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

    __table_args__ = (
        UniqueConstraint('sender_id', 'recipient_id',
                         name='uq_sender_recipient'),
    )
