from app.infrastructure.config.database import Base
from sqlalchemy import (
    String,
    ForeignKey,
    BIGINT,
    UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Room(Base):
    """
    Represents a chat room.
    Attributes:
        room_id (str): A unique identifier for the room.
        sender_id (int): The ID of the user who initiated the chat.
        recipient_id (int): The ID of the user who is the recipient of the chat.
        sender (User): The user who initiated the chat (foreign key to the User table).
        recipient (User): The recipient of the chat (foreign key to the User table).
    Constraints:
        UniqueConstraint: Ensures that there can only be one chat room for a specific sender-recipient pair.
    """
    room_id: Mapped[str] = mapped_column(String(length=250))
    sender_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('user.id'))
    recipient_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('user.id'))
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

    __table_args__ = (
        UniqueConstraint('sender_id', 'recipient_id',
                         name='uq_sender_recipient'),
    )
