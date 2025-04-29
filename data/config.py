from pathlib import Path

from environs import Env

env = Env()
env.read_env()

DIR = Path(__file__).absolute().parent.parent


TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN", None)


RD_DB = env.int("RD_DB", None)
RD_HOST = env.str("RD_HOST", None)
RD_PORT = env.int("RD_PORT", None)
RD_USER = env.str("RD_USER", None)
RD_PASS = env.str("RD_PASS", None)

RD_URI = env.str("RD_URI", default=None)
if RD_DB and RD_HOST and RD_PORT:
    RD_URI = f"redis://{RD_HOST}:{RD_PORT}/{RD_DB}"
    if RD_USER and RD_PASS:
        RD_URI = f"redis://{RD_USER}:{RD_PASS}@{RD_HOST}:{RD_PORT}/{RD_DB}"


SURREAL_NS = env.str("SURREAL_NS", "test")
SURREAL_DB = env.str("SURREAL_DB", "test")
SURREAL_USER = env.str("SURREAL_USER", None)
SURREAL_PASS = env.str("SURREAL_PASS", None)

SURREAL_URL = env.str("SURREAL_URL", "ws://localhost:8000")


I18N_PATH = f"{DIR}/data/locales"
I18N_DOMAIN = env.str("I18N_DOMAIN", "bot")
