from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class SongsCallback(CallbackData, prefix="songs"):
    data: str
    id: str
    key: str


def get_songs_markup(
    data: str,
    key: str,
    songs: list[any],
):
    builder = InlineKeyboardBuilder()

    buttons = [
        InlineKeyboardButton(text=f"{i + 1}", callback_data=SongsCallback(data=data, id=s.id, key=key).pack()) for i, s in enumerate(songs)
    ]
    builder.add(*buttons)
    builder.adjust(2)

    return builder.as_markup()
