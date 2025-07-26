from contextlib import suppress

from aiogram import F
from aiogram.types import CallbackQuery

from app.api import get_text
from app.handlers.users.search import get_song_state
from app.keyboards import SongCallback, get_songs_markup, get_song_markup, SongsCallback
from database.models import User
from loader import dp, _, bot


@dp.callback_query(SongsCallback.filter())
async def select_song_(call: CallbackQuery, callback_data: SongsCallback, user: User, session):
    song = await get_song_state(callback_data.id, user, session)

    if song.text:
        library = song in user.songs
        text = get_text(song.text, chords=False)
        markup = get_song_markup(callback_data.data, song.id, library=library)
        return await call.message.edit_text(text, reply_markup=markup)
    return await call.answer(_("Looks like the song has no lyrics"), show_alert=True)


@dp.callback_query(SongCallback.filter(F.data.regexp(r"search") & F.action.regexp(r"back")))
async def back_to_result_(call: CallbackQuery, user: User):
    songs = user.history

    if songs:
        text = _("Select song:") + "\n"
        for i, s in enumerate(songs):
            text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"
        return await call.message.edit_text(text, reply_markup=get_songs_markup("search", songs))
    return await call.message.edit_text(_("Looks like the songs are out of memory or you used /cancel"),
                                        reply_markup=None)


@dp.callback_query(SongCallback.filter(F.action.startswith("chords")))
async def song_chords_(call: CallbackQuery, callback_data: SongCallback, user: User, session):
    song = await get_song_state(callback_data.id, user, session)

    chords = eval(callback_data.action[7:])
    library = song in user.songs

    with suppress(Exception):
        if call.inline_message_id:
            await bot.edit_message_text(inline_message_id=call.inline_message_id,
                                        text=get_text(song.text, chords),
                                        reply_markup=get_song_markup("", id=song.id, chords=chords, inline=True))
        else:
            await call.message.edit_text(get_text(song.text, chords),
                                         reply_markup=get_song_markup(callback_data.data, song.id, chords=chords,
                                                                      library=library))


@dp.callback_query(SongCallback.filter(F.action.regexp(r"music")))
async def song_music_(call: CallbackQuery, callback_data: SongCallback, user: User, session):
    song = await get_song_state(callback_data.id, user, session)

    if song.file != "":
        return await call.message.answer_audio(audio=song.file)
    return await call.answer(_("Looks like there’s no music on the resource for this song"), show_alert=True)


@dp.callback_query(SongCallback.filter(F.action.startswith("library")))
async def song_library_(call: CallbackQuery, callback_data: SongCallback, user: User, session):
    song = await get_song_state(callback_data.id, user, session)

    chords = eval(SongCallback.unpack(call.message.reply_markup.inline_keyboard[0][0].callback_data).action[7:])
    library = eval(callback_data.action[8:])
    if library:
        user.songs.append(song)
        await session.commit()
    else:
        user.songs.remove(song)
        await session.commit()

    return await call.message.edit_reply_markup(
        reply_markup=get_song_markup(callback_data.data, song.id, chords=not chords, library=library))
