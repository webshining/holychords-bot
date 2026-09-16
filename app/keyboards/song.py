from aiogram.enums.button_style import ButtonStyle
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from loader import _


class SongCallback(CallbackData, prefix="song"):
    data: str
    id: str
    action: str
    key: str


def get_song_markup(data: str, id: str, key: str, chords: bool = False, library: bool = False, inline: bool = False):
    markup = InlineKeyboardBuilder()

    markup.add(
        InlineKeyboardButton(
            text=_("Chords"),
            style=ButtonStyle.SUCCESS if chords else ButtonStyle.DANGER,
            callback_data=SongCallback(data=data, id=id, key=key, action=f"chords_{not chords}").pack(),
        )
    )
    if not inline:
        markup.add(InlineKeyboardButton(text=_("Music"), callback_data=SongCallback(data=data, id=id, key=key, action="music").pack()))
        markup.row(
            InlineKeyboardButton(
                text=_("In library"),
                style=ButtonStyle.SUCCESS if library else ButtonStyle.DANGER,
                callback_data=SongCallback(data=data, id=id, key=key, action=f"library_{not library}").pack(),
            )
        )
    markup.row(InlineKeyboardButton(text=_("Back"), callback_data=SongCallback(data=data, id="", key=key, action="back").pack()))

    return markup.as_markup()
