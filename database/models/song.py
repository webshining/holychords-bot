from typing import List

from sqlalchemy import Integer, String, Table, Column, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel

user_song = Table(
    "user_song",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("song_id", ForeignKey("songs.id"), primary_key=True)
)
user_history = Table(
    "user_history",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("song_id", ForeignKey("songs.id"), primary_key=True)
)


class Song(BaseModel):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[str] = mapped_column(String, nullable=False)
    file: Mapped[str] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    users: Mapped[List["User"]] = relationship(back_populates="songs", secondary=user_song)
    history: Mapped[List["User"]] = relationship(back_populates="history", secondary=user_history)
