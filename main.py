from aiogram import executor
from app.handlers import dp


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=print('Bot started!'))
    