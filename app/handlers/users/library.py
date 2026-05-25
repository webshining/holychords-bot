from aiogram import F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from common import common_pb2
from songs.songs_pb2_grpc import SongsServiceStub

from app.keyboards import SongCallback, get_songs_markup
from database.models import User
from loader import _, dp


@dp.message(Command("library"))
async def library_(message: Message, user: User, songs: SongsServiceStub):
    response = await songs.GetLibrary(common_pb2.Empty(), metadata=[("user_id", str(user.id))])

    text = _("Select song:") + "\n"
    for i, s in enumerate(response.songs):
        text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"

    await message.answer(text, reply_markup=get_songs_markup("library", response.songs))


@dp.callback_query(SongCallback.filter((F.data == "library") & (F.action == "back")))
async def back_to_library_(call: CallbackQuery, user: User, songs: SongsServiceStub):
    response = await songs.GetLibrary(common_pb2.Empty(), metadata=[("user_id", str(user.id))])

    text = _("Select song:") + "\n"
    for i, s in enumerate(response.songs):
        text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"
    await call.message.edit_text(text, reply_markup=get_songs_markup("library", response.songs))
