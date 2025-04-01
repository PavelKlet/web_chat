from datetime import datetime

from infrastructure.database import Base
from sqlalchemy import (
    String,
    ForeignKey,
    BIGINT,
    UniqueConstraint,
    JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Message(Base):
    text = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    room_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('room.id'))


class Room(Base):
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
