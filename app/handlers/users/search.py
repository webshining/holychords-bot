from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.api import get_songs
from app.keyboards import get_songs_markup
from app.states import SearchState
from database.models import Song, User
from loader import _, dp


async def get_song_state(id: int, user: User, session):
    songs = user.history
    song = next((i for i in songs if i.id == id), None)

    if not song:
        song = await Song.get(id=id, session=session)
        if song:
            user.history.append(song)
            await session.commit()

    return song


@dp.message(Command("search"))
async def search_(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(SearchState.name)
    return await message.answer(_("Enter song name:"))


@dp.message(SearchState.name)
@dp.message(F.text, ~F.text.startswith("/"))
async def search_name_(message: Message, state: FSMContext, user: User, session):
    songs = await get_songs(message.text, session)
    user.history = songs
    await session.commit()
    await message.delete()

    if songs:
        text = _("Select song:") + "\n"
        for i, s in enumerate(songs):
            text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"
        markup = get_songs_markup("search", songs)
    else:
        text, markup = _("A song with this name was not found, try another:"), None

    await state.set_state(None)
    await message.answer(text, reply_markup=markup)
