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
        session = data['session']
        if event.message:
            await self.handle_message(event.message, session, data)
        elif event.callback_query:
            await self.handle_callback_query(event.callback_query, session, data)
        elif event.inline_query:
            await self.handle_inline_query(event.inline_query, session, data)
        await handler(event, data)

    @staticmethod
    async def handle_message(message: Message, session, data: Dict[str, Any]):
        user = await User.get(message.from_user.id, session=session)
        if not user:
            user = await User.create(id=message.from_user.id, name=message.from_user.full_name,
                                     username=message.from_user.username, session=session, history=[],
                                     songs=[])
        else:
            user = await User.update(id=message.from_user.id, name=message.from_user.full_name,
                                     username=message.from_user.username, session=session)
        data["user"] = user

    @staticmethod
    async def handle_callback_query(call: CallbackQuery, session, data: Dict[str, Any]):
        await call.answer()
        user = await User.get(call.from_user.id, session=session)
        if not user:
            user = await User.create(id=call.from_user.id, name=call.from_user.full_name,
                                     username=call.from_user.username, session=session, history=[],
                                     songs=[])
        else:
            user = await User.update(id=call.from_user.id, name=call.from_user.full_name,
                                     username=call.from_user.username, session=session)
        data["user"] = user

    @staticmethod
    async def handle_inline_query(query: InlineQuery, session, data: Dict[str, Any]):
        user = await User.get(query.from_user.id, session=session)
        if not user:
            user = await User.create(id=query.from_user.id, name=query.from_user.full_name,
                                     username=query.from_user.username, session=session, history=[],
                                     songs=[])
        else:
            user = await User.update(id=query.from_user.id, name=query.from_user.full_name,
                                     username=query.from_user.username, session=session)
        data["user"] = user
