from typing import List

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .song import user_song, user_history
from ..base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="user")
    songs: Mapped[List["Song"]] = relationship(back_populates="users", lazy="joined", secondary=user_song)
    history: Mapped[List["Song"]] = relationship(back_populates="history", lazy="joined", secondary=user_history)
