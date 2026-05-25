from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from songs import songs_pb2
from songs.songs_pb2_grpc import SongsServiceStub

from app.keyboards import get_song_markup
from database.models import User
from loader import dp
from app.services import song_text


@dp.inline_query()
async def inline_handler(query: InlineQuery, user: User, songs: SongsServiceStub):
    results = []
    if query.query:
        songs = await songs.Search(
            songs_pb2.SearchRequest(input=query.query, source=songs_pb2.Source.HOLYCHORDS), metadata=[("user_id", str(user.id))]
        )
        for i, song in enumerate(songs.songs):
            if song.text:
                results.append(
                    InlineQueryResultArticle(
                        id=f"{i}",
                        title=f"{song.name} - {song.artist}",
                        description=song.artist,
                        input_message_content=InputTextMessageContent(message_text=song_text(song.text)),
                        reply_markup=get_song_markup("", id=song.id, inline=True),
                    )
                )

    await query.answer(results=results, is_personal=True, cache_time=2)
