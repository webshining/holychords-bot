from aiogram import F
from aiogram.filters import Command
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, Message
from songs import songs_pb2

from app.keyboards import get_songs_markup
from database.models import User
from loader import _, dp


@dp.message(Command("search"))
async def search_(message: Message):
    await message.delete()
    return await message.answer(_("Enter song name:"))


@dp.message(F.text, ~F.text.startswith("/"))
async def search_query_(message: Message, user: User, songs):
    query = message.text.replace(f"@{(await message.bot.me()).username}", "").strip()
    response = await songs.Search(
        songs_pb2.SearchRequest(input=query, source=songs_pb2.Source.HOLYCHORDS), metadata=[("user_id", str(user.id))]
    )

    if response.songs:
        text = _("Select song:") + "\n"
        for i, s in enumerate(response.songs):
            text += f"\n<b>{i + 1}.</b> <u>{s.name}</u> - {s.artist}"
        markup = get_songs_markup("search", response.songs)
    else:
        text, markup = _("A song with this name was not found, try another:"), None

    if message.answer_guest_query:
        return await message.answer_guest_query(
            InlineQueryResultArticle(
                id=query, title=query, input_message_content=InputTextMessageContent(message_text=text), reply_markup=markup
            )
        )
    await message.answer(text, reply_markup=markup)
