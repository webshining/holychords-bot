from aiogram.types import Message

from database.models import User
from loader import dp

from .search import search_query_


@dp.guest_message()
async def guest_message_(message: Message, user: User, songs):
    await search_query_(message, user, songs)
