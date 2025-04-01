from sqlalchemy import (
    String,
    ForeignKey,
    BIGINT,
    Table,
    Column,
    UniqueConstraint,
    Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base


friends = Table(
    "friends",
    Base.metadata,
    Column("id", BIGINT, primary_key=True),
    Column("user_id", BIGINT, ForeignKey("user.id")),
    Column("friend_id", BIGINT, ForeignKey("user.id")),
    UniqueConstraint("user_id", "friend_id", name="unique_user_friend"),
)


class Profile(Base):
    first_name: Mapped[str] = mapped_column(String(length=60), nullable=True)
    last_name: Mapped[str] = mapped_column(String(length=60), nullable=True)
    avatar: Mapped[str] = mapped_column(String(length=255), nullable=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="profile")


class User(Base):
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    username: Mapped[str] = mapped_column(String(length=50), nullable=False,
                                          index=True)
    profile: Mapped["Profile"] = relationship(back_populates="user")
    friends: Mapped["User"] = relationship(
        "User",
        secondary="friends",
        primaryjoin="User.id == friends.c.user_id",
        secondaryjoin="User.id == friends.c.friend_id",
    )
    email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)