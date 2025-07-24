from aiogram import Dispatcher

from .database import DatabaseMiddleware
from .inter import i18n_middleware
from .user import UserMiddleware


def setup_middlewares(dp: Dispatcher):
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(i18n_middleware)
    dp.update.middleware(UserMiddleware())
