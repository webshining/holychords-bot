from pathlib import Path

from environs import Env

env = Env()
env.read_env()

DIR = Path(__file__).absolute().parent.parent

TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN", None)
WEBHOOK_URL = env.str("WEBHOOK_URL", default=None)
WEBHOOK_PATH = env.str("WEBHOOK_PATH", default=None)
WEBHOOK_SERVER_HOST = env.str("WEBHOOK_SERVER_HOST", default=None)
WEBHOOK_SERVER_PORT = env.int("WEBHOOK_SERVER_PORT", default=None)
WEBHOOK_SERVER_SECRET = env.str("WEBHOOK_SERVER_SECRET", default=None)

RD_URI = env.str("RD_URI", default=None)

DB_URI = env.str("DB_URI", default="sqlite+aiosqlite:///database.sqlite3")

I18N_PATH = f"{DIR}/data/locales"
I18N_DOMAIN = "bot"

SONGS_ENDPOINT = env.str("SONGS_ENDPOINT", default="127.0.0.1:4000")
