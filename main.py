import asyncio
import signal

import grpc.aio as grpc
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from loguru import logger
from songs import songs_pb2_grpc

from app import set_default_commands, setup_middlewares
from data.config import (
    SONGS_ENDPOINT,
    WEBHOOK_PATH,
    WEBHOOK_SERVER_HOST,
    WEBHOOK_SERVER_PORT,
    WEBHOOK_SERVER_SECRET,
    WEBHOOK_URL,
)
from loader import bot, dp


async def on_startup() -> None:
    await set_default_commands()
    if all([WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SERVER_SECRET]):
        await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SERVER_SECRET)
    else:
        await bot.delete_webhook()

    channel = grpc.insecure_channel(SONGS_ENDPOINT)
    songs_client = songs_pb2_grpc.SongsServiceStub(channel)

    dp["songs"] = songs_client


async def on_shutdown() -> None:
    logger.info("Bot stopped!")


async def main() -> None:
    setup_middlewares(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    if all([WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SERVER_SECRET, WEBHOOK_SERVER_PORT, WEBHOOK_SERVER_HOST]):
        app = web.Application()
        webhook_request_headers = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SERVER_SECRET)
        webhook_request_headers.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host=WEBHOOK_SERVER_HOST, port=WEBHOOK_SERVER_PORT)
        await site.start()

        logger.info("Webhook started!")

        stop_event = asyncio.Event()

        def signal_handler():
            logger.info("Received stop signal, shutting down...")
            stop_event.set()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)

        try:
            await stop_event.wait()
        finally:
            await runner.cleanup()
    else:
        logger.info("Bot polling started!")
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by KeyboardInterrupt")
    except Exception as e:
        logger.exception(f"Bot crashed with error: {e}")
