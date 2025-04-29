import pickle

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.api import get_songs, get_song
from app.keyboards import get_songs_markup
from app.states import SearchState
from loader import _, dp


async def get_song_state(id: int, state: FSMContext):
    data = await state.get_data()
    songs = data.get("songs")
    songs = pickle.loads(bytes.fromhex(songs)) if songs else []
    song = next((i for i in songs if i.id == id), None)

    if not song:
        song = await get_song(id)
        await state.update_data(songs=pickle.dumps([*songs, song]).hex())

    return song


@dp.message(Command("search"))
async def search_(message: Message, state: FSMContext):
    await state.set_state(SearchState.name)
    return await message.answer(_("Enter song name:"))


@dp.message(SearchState.name)
@dp.message(F.text)
async def search_name_(message: Message, state: FSMContext):
    songs = await get_songs(message.text)

    if songs:
        text = _("Select song:") + "\n"
        for i, s in enumerate(songs):
            text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"
        markup = get_songs_markup("search", songs)
        await state.clear()
        await state.update_data(songs=pickle.dumps(songs).hex())
    else:
        text, markup = _("A song with this name was not found, try another:"), None

    return await message.answer(text, reply_markup=markup)
