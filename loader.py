from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import I18n

from data.config import (I18N_DOMAIN, I18N_PATH, RD_DB, RD_HOST, RD_PASS,
                         RD_PORT, TELEGRAM_BOT_TOKEN)

bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")
if RD_DB and RD_HOST and RD_PORT:
    from aiogram.fsm.storage.redis import RedisStorage
    from redis.asyncio.client import Redis
    storage = RedisStorage(Redis(db=RD_DB, host=RD_HOST, port=RD_PORT, password=RD_PASS))
else:
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()
dp = Dispatcher(storage=storage)



i18n = I18n(path=I18N_PATH, domain=I18N_DOMAIN)
_ = i18n.gettext
