import nanoid
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from songs.v2 import songs_pb2 as songs_v2

from app.keyboards import get_song_markup
from app.services import song_text
from database.models import User
from loader import dp


@dp.inline_query()
async def inline_handler(query: InlineQuery, user: User, songs):
    results = []
    if query.query:
        response = await songs.v2.Search(
            songs_v2.SearchRequest(input=query.query, source=songs_v2.Source.HOLYCHORDS), metadata=[("user_id", str(user.id))]
        )
        for song in response.songs:
            if song.text:
                results.append(
                    InlineQueryResultArticle(
                        id=nanoid.generate(),
                        title=f"{song.name} - {song.artist}",
                        description=song.artist,
                        input_message_content=InputTextMessageContent(message_text=song_text(song.text)),
                        reply_markup=get_song_markup("search", song.id, response.key, inline=True),
                    )
                )

    await query.answer(results=results, is_personal=True, cache_time=2)
