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

from app.infrastructure.database import Base


friends = Table(
    "friends",
    Base.metadata,
    Column("id", BIGINT, primary_key=True),
    Column("user_id", BIGINT, ForeignKey("user.id")),
    Column("friend_id", BIGINT, ForeignKey("user.id")),
    UniqueConstraint("user_id", "friend_id", name="unique_user_friend"),
)

"""
Defines a many-to-many relationship between users representing friendships.
Attributes:
    id (int): The primary key of the record.
    user_id (int): The ID of the user initiating the friendship.
    friend_id (int): The ID of the user who is the friend.
Constraints:
    unique_user_friend: Ensures unique user-friend pairs.
"""


class Profile(Base):
    """
    Represents a user's profile.
    Attributes:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        avatar (str): The URL of the user's avatar.
        user_id (int): The ID of the user associated with this profile.
        user (User): The user associated with this profile.
    """
    first_name: Mapped[str] = mapped_column(String(length=60), nullable=True)
    last_name: Mapped[str] = mapped_column(String(length=60), nullable=True)
    avatar: Mapped[str] = mapped_column(String(length=255), nullable=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="profile")


class User(Base):
    """
   Represents a user in the system.
   Attributes:
       email (str): The email address of the user. Must be unique.
       hashed_password (str): The hashed password of the user.
       username (str): The username of the user.
       profile (Profile): The user's profile.
       friends (List[User]): A list of the user's friends.
       email_confirmed (bool): Indicates whether the user's email is confirmed.
   Relationships:
       profile: One-to-one relationship with the Profile model.
       friends: Many-to-many relationship with other User instances through the 'friends' table.
   """
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