from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.i18n import I18n
from songs.v1 import songs_pb2_grpc as songs_v1_grpc
from songs.v2 import songs_pb2_grpc as songs_v2_grpc

from data.config import I18N_DOMAIN, I18N_PATH, RD_URI, TELEGRAM_BOT_TOKEN


@dataclass(slots=True)
class SongsClients:
    v1: songs_v1_grpc.SongsServiceStub
    v2: songs_v2_grpc.SongsServiceStub


bot = Bot(
    TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True),
)

if RD_URI:
    from aiogram.fsm.storage.redis import RedisStorage
    from redis.asyncio.client import Redis

    storage = RedisStorage(Redis.from_url(RD_URI))
else:
    from aiogram.fsm.storage.memory import MemoryStorage

    storage = MemoryStorage()
dp = Dispatcher(storage=storage)

i18n = I18n(path=I18N_PATH, domain=I18N_DOMAIN)
_ = i18n.gettext
_lazy = i18n.lazy_gettext
