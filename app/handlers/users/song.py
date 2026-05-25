from contextlib import suppress

from aiogram import F
from aiogram.types import CallbackQuery
from common import common_pb2
from songs import songs_pb2
from songs.songs_pb2_grpc import SongsServiceStub

from app.keyboards import SongCallback, SongsCallback, get_song_markup, get_songs_markup
from app.services import get_song, song_text
from database.models import User
from loader import _, bot, dp


@dp.callback_query(SongsCallback.filter())
async def select_song_(call: CallbackQuery, callback_data: SongsCallback, user: User, songs: SongsServiceStub):
    try:
        song = await get_song(songs, str(user.id), callback_data.id)
    except Exception as e:
        return await call.answer(str(e), show_alert=True)

    if song.text:
        text = song_text(song.text, chords=False)
        markup = get_song_markup(callback_data.data, song.id, library=song.in_library)
        return await call.message.edit_text(text, reply_markup=markup)
    return await call.answer(_("Looks like the song has no lyrics"))


@dp.callback_query(SongCallback.filter(F.data.regexp(r"search") & F.action.regexp(r"back")))
async def back_to_result_(call: CallbackQuery, user: User, songs: SongsServiceStub):
    response = await songs.GetHistory(common_pb2.Empty(), metadata=[("user_id", str(user.id))])

    if response.songs:
        text = _("Select song:") + "\n"
        for i, s in enumerate(response.songs):
            text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"
        return await call.message.edit_text(text, reply_markup=get_songs_markup("search", response.songs))
    return await call.message.edit_text(_("Looks like the songs are out of memory"), reply_markup=None)


@dp.callback_query(SongCallback.filter(F.action.startswith("chords")))
async def song_chords_(call: CallbackQuery, callback_data: SongCallback, user: User, songs: SongsServiceStub):
    try:
        song = await get_song(songs, str(user.id), callback_data.id)
    except Exception as e:
        return await call.answer(str(e), show_alert=True)

    chords = eval(callback_data.action[7:])

    with suppress(Exception):
        if call.inline_message_id:
            await bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                text=song_text(song.text, chords),
                reply_markup=get_song_markup("", id=song.id, chords=chords, inline=True),
            )
        else:
            await call.message.edit_text(
                song_text(song.text, chords),
                reply_markup=get_song_markup(callback_data.data, song.id, chords=chords, library=song.in_library),
            )


@dp.callback_query(SongCallback.filter(F.action.regexp(r"music")))
async def song_music_(call: CallbackQuery, callback_data: SongCallback, user: User, songs: SongsServiceStub):
    try:
        song = await get_song(songs, str(user.id), callback_data.id)
    except Exception as e:
        return await call.answer(str(e), show_alert=True)

    if song.file != "":
        await call.message.answer_audio(audio=f"https://holychords.pro{song.file}")
        return await call.answer()
    return await call.answer(_("Looks like there's no music on the resource for this song"))


@dp.callback_query(SongCallback.filter(F.action.startswith("library")))
async def song_library_(call: CallbackQuery, callback_data: SongCallback, user: User, songs: SongsServiceStub):
    try:
        song = await get_song(songs, str(user.id), callback_data.id)
    except Exception as e:
        return await call.answer(str(e), show_alert=True)

    chords = eval(SongCallback.unpack(call.message.reply_markup.inline_keyboard[0][0].callback_data).action[7:])
    if not song.in_library:
        await songs.AddToLibrary(
            songs_pb2.AddToLibraryRequest(id=callback_data.id, source=songs_pb2.Source.HOLYCHORDS), metadata=[("user_id", str(user.id))]
        )
    else:
        await songs.RemoveFromLibrary(
            songs_pb2.RemoveFromLibraryRequest(id=callback_data.id, source=songs_pb2.Source.HOLYCHORDS),
            metadata=[("user_id", str(user.id))],
        )

    with suppress(Exception):
        await call.answer()
        return await call.message.edit_reply_markup(
            reply_markup=get_song_markup(callback_data.data, song.id, chords=not chords, library=not song.in_library)
        )
