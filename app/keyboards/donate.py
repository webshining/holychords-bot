from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DonateCallback(CallbackData, prefix="donate"):
    amount: int


def get_donate_markup(amount: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"{amount} XTR",
        pay=True
    )

    return builder.as_markup()
