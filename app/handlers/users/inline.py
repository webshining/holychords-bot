from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from app.api import get_songs, get_text
from loader import dp


@dp.inline_query()
async def inline_handler(query: InlineQuery, session):
    results = []
    if query.query:
        for i, song in enumerate(await get_songs(query.query, session)):
            if song.text:
                results.append(InlineQueryResultArticle(
                    id=f'{i}',
                    title=f'{song.name} - {song.artist}',
                    description=song.artist,
                    input_message_content=InputTextMessageContent(message_text=get_text(song.text, True))
                ))

    await query.answer(results=results, is_personal=True, cache_time=2)
