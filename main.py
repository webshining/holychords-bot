from aiogram import executor
from aiogram.types import BotCommandScopeDefault
from app.middlewares.inter import i18n
from loader import dp, bot


async def on_startup(dispatcher):
    from app.middlewares import setup_middlewares
    from app.commands import set_default_commands
    setup_middlewares(dp)
    await set_default_commands()


async def on_shutdown(dispatcher):
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
    for lang in i18n.available_locales:
        await bot.delete_my_commands(scope=BotCommandScopeDefault(), language_code=lang)


if __name__ == '__main__':
    import app.handlers
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
