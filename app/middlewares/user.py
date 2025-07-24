from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery, InlineQuery

from database.models import User


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ):
        if event.message:
            await self.handle_message(event.message, data)
        elif event.callback_query:
            await self.handle_callback_query(event.callback_query, data)
        elif event.inline_query:
            await self.handle_inline_query(event.inline_query, data)
        await handler(event, data)

    @staticmethod
    async def handle_message(message: Message, data: Dict[str, Any]):
        session = data['session']
        data['user'] = await User.update_or_create(id=message.from_user.id, name=message.from_user.full_name,
                                                   username=message.from_user.username, session=session, history=[],
                                                   songs=[])

    @staticmethod
    async def handle_callback_query(call: CallbackQuery, data: Dict[str, Any]):
        await call.answer()
        session = data['session']
        data['user'] = await User.update_or_create(id=call.from_user.id, name=call.from_user.full_name,
                                                   username=call.from_user.username, session=session, history=[],
                                                   songs=[])

    @staticmethod
    async def handle_inline_query(query: InlineQuery, data: Dict[str, Any]):
        session = data['session']
        data['user'] = await User.update_or_create(id=query.from_user.id, name=query.from_user.full_name,
                                                   username=query.from_user.username, session=session, history=[],
                                                   songs=[])
