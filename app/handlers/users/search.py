from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards import get_songs_markup, get_song_markup
from app.states import Search
from loader import dp, _
from utils import get_songs


@dp.message(Command('search'))
async def search_(message: Message, state: FSMContext):
    await message.answer(_("Enter song name:"))
    await state.set_state(Search.name)


@dp.message()
@dp.message(Search.name)
async def search_name_(message: Message, state: FSMContext):
    songs = await get_songs(message.text)
    if songs:
        text = _("Select song:") + "\n"
        for i, s in enumerate(songs):
            text += f'\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}'
        await message.answer(text, reply_markup=get_songs_markup('search', songs))
        await state.clear()
        await state.update_data(songs=songs)
    else:
        await message.answer(_("A song with this name was not found, try another:"))


@dp.callback_query(lambda call: call.data.startswith('search'))
async def search_callback_(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    songs = data.get('songs') or []
    song = list(filter(lambda s: s.id == int(call.data[7:]), songs))
    if song:
        await call.message.edit_text(song[0].get_text(chords=False), reply_markup=get_song_markup("song", song[0].id))
    else:
        await call.message.edit_text(_("Looks like the songs are out of memory or you used /cancel"))


@dp.callback_query(lambda call: call.data.startswith('song'))
async def song_callback_(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    songs = data.get('songs') or []
    if call.data[5:] == 'back':
        if songs:
            text = "Select song:\n"
            for i, s in enumerate(songs):
                text += f'\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}'
            await call.message.edit_text(text, reply_markup=get_songs_markup('search', songs))
        else:
            await call.message.edit_text(_("Looks like the songs are out of memory or you used /cancel"),
                                         reply_markup=None)
            await state.clear()
    elif call.data[5:].startswith("chords"):
        chords, id = call.data[12:].split("_")
        song = list(filter(lambda s: s.id == int(id), songs))
        if song:
            await call.message.edit_text(song[0].get_text(eval(chords)),
                                         reply_markup=get_song_markup("song", song[0].id, not eval(chords)))
        else:
            await call.message.edit_text(_("Looks like the songs are out of memory or you used /cancel"),
                                         reply_markup=None)
    elif call.data[5:].startswith("music"):
        song = list(filter(lambda s: s.id == int(call.data[11:]), songs))
        if song:
            await call.answer()
            if song[0].file:
                await call.message.answer_audio(audio=song[0].file)
            else:
                await call.message.answer(_("Looks like there’s no music on the resource for this song"))
        else:
            await call.message.edit_text(_("Looks like the songs are out of memory or you used /cancel"),
                                         reply_markup=None)
