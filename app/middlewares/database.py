from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update

from database import get_session


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Update, dict[str, Any]], Awaitable[Any]], event: Update, data: dict[str, Any]):
        async with get_session() as session:
            data["session"] = session
            await handler(event, data)
