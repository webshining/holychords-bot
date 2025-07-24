from pathlib import Path

from environs import Env

env = Env()
env.read_env()

DIR = Path(__file__).absolute().parent.parent

TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN", None)

RD_URI = env.str("RD_URI", default=None)

DB_URI = env.str("DB_URI", default="sqlite+aiosqlite:///database.sqlite3")

I18N_PATH = f"{DIR}/data/locales"
I18N_DOMAIN = env.str("I18N_DOMAIN", "bot")
