from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from songs import songs_pb2

from app.keyboards import get_songs_markup
from app.states import SearchState
from database.models import User
from loader import _, dp


@dp.message(Command("search"))
async def search_(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(SearchState.name)
    return await message.answer(_("Enter song name:"))


@dp.message(SearchState.name)
@dp.message(F.text, ~F.text.startswith("/"))
async def search_name_(message: Message, state: FSMContext, user: User, session, songs):
    response = await songs.Search(
        songs_pb2.SearchRequest(input=message.text, source=songs_pb2.Source.HOLYCHORDS), metadata=[("user_id", str(user.id))]
    )

    if response.songs:
        text = _("Select song:") + "\n"
        for i, s in enumerate(response.songs):
            text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"
        markup = get_songs_markup("search", response.songs)
    else:
        text, markup = _("A song with this name was not found, try another:"), None

    await state.set_state(None)
    await message.answer(text, reply_markup=markup)
