### <p align="center"><a href="https://core.telegram.org/bots/api">Telegram Bot</a> with <a href="https://docs.aiogram.dev/en/dev-3.x/">aiogram</a>

---

- [Init project](#init-project)
- [Configure environment variables](#configure-environment-variables)
- [Bot config](#bot-config)
- [Redis config](#redis-config)
- [Database config](#database-config)
- [Songs config](#songs-config)
- [Application start](#application-start)

## Init project

```bash
$ git clone https://github.com/webshining/holychords-bot project_name
$ cd project_name
$ uv sync
```

## Configure environment variables

> Copy variables from .env.ren file to .env

```bash
$ cp .env.ren .env
```

## Bot config

`TELEGRAM_BOT_TOKEN` - your bot token (required)

`WEBHOOK_URL` - url to your webhook server (https://example.com) [for telegram]

`WEBHOOK_PATH` - url path to your bot in webhook server (/mybot) [for telegram]

`WEBHOOK_SERVER_HOST` - host for start webhook server

`WEBHOOK_SERVER_PORT` - port for start webhook server

## Redis config

> If you are not using redis, by default used MemoryStorage

`RD_URI` - connection url to your redis server

## Database config

> If not provided by default used sqlite3

`DB_URI` - connection url to your database (postgresql+asyncpg://admin:admin@127.0.0.1:5432/mybot)

## Songs config

`SONGS_ENDPOINT` - endpoint of songs grpc service (127.0.0.1:4003)

## Application start

```bash
$ uv run main.py
```
