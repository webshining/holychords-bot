from contextlib import suppress

from aiogram import F
from aiogram.types import CallbackQuery
from songs.v1 import songs_pb2 as songs_v1
from songs.v2 import songs_pb2 as songs_v2

from app.keyboards import SongCallback, SongsCallback, get_song_markup, get_songs_markup
from app.services import get_song, song_text
from database.models import User
from loader import _, bot, dp


@dp.callback_query(SongsCallback.filter())
async def select_song_(call: CallbackQuery, callback_data: SongsCallback, user: User, songs):
    try:
        song = await get_song(songs, str(user.id), callback_data.id)
    except Exception as e:
        return await call.answer(str(e), show_alert=True)

    text, markup = _("Looks like the song has no lyrics"), None
    if song.text:
        text = song_text(song.text, chords=False)
        markup = get_song_markup(
            callback_data.data, song.id, callback_data.key, library=song.in_library, inline=call.inline_message_id is not None
        )

    if call.inline_message_id:
        return await call.bot.edit_message_text(text, reply_markup=markup, inline_message_id=call.inline_message_id)
    return await call.message.edit_text(text, reply_markup=markup)


@dp.callback_query(SongCallback.filter(F.data.regexp(r"search") & F.action.regexp(r"back")))
async def back_to_result_(call: CallbackQuery, callback_data: SongCallback, user: User, songs):
    response = await songs.v2.GetHistory(songs_v2.GetHistoryRequest(key=callback_data.key), metadata=[("user_id", str(user.id))])

    if response.songs:
        text = _("Select song:") + "\n"
        for i, s in enumerate(response.songs):
            text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"
        markup = get_songs_markup(callback_data.data, response.key, response.songs)
    else:
        text, markup = _("Looks like the songs are out of memory"), None

    with suppress(Exception):
        if call.inline_message_id:
            await bot.edit_message_text(inline_message_id=call.inline_message_id, text=text, reply_markup=markup)
        else:
            await call.message.edit_text(text, reply_markup=markup)


@dp.callback_query(SongCallback.filter(F.action.startswith("chords")))
async def song_chords_(call: CallbackQuery, callback_data: SongCallback, user: User, songs):
    try:
        song = await get_song(songs, str(user.id), callback_data.id)
    except Exception as e:
        return await call.answer(str(e), show_alert=True)

    chords = eval(callback_data.action[7:])
    text, markup = song_text(song.text, chords), get_song_markup(
        callback_data.data, song.id, callback_data.key, chords=chords, inline=call.inline_message_id is not None
    )

    with suppress(Exception):
        if call.inline_message_id:
            await bot.edit_message_text(inline_message_id=call.inline_message_id, text=text, reply_markup=markup)
        else:
            await call.message.edit_text(text, reply_markup=markup)


@dp.callback_query(SongCallback.filter(F.action.regexp(r"music")))
async def song_music_(call: CallbackQuery, callback_data: SongCallback, user: User, songs):
    try:
        song = await get_song(songs, str(user.id), callback_data.id)
    except Exception as e:
        return await call.answer(str(e), show_alert=True)

    if song.file != "":
        await call.message.answer_audio(audio=f"https://holychords.pro{song.file}")
        return await call.answer()
    return await call.answer(_("Looks like there's no music on the resource for this song"))


@dp.callback_query(SongCallback.filter(F.action.startswith("library")))
async def song_library_(call: CallbackQuery, callback_data: SongCallback, user: User, songs):
    try:
        song = await get_song(songs, str(user.id), callback_data.id)
    except Exception as e:
        return await call.answer(str(e), show_alert=True)

    chords = eval(SongCallback.unpack(call.message.reply_markup.inline_keyboard[0][0].callback_data).action[7:])
    if not song.in_library:
        await songs.v1.AddToLibrary(
            songs_v1.AddToLibraryRequest(id=callback_data.id, source=songs_v1.Source.HOLYCHORDS), metadata=[("user_id", str(user.id))]
        )
    else:
        await songs.v1.RemoveFromLibrary(
            songs_v1.RemoveFromLibraryRequest(id=callback_data.id, source=songs_v1.Source.HOLYCHORDS),
            metadata=[("user_id", str(user.id))],
        )

    with suppress(Exception):
        await call.answer()
        return await call.message.edit_reply_markup(
            reply_markup=get_song_markup(callback_data.data, song.id, callback_data.key, chords=not chords, library=not song.in_library)
        )
