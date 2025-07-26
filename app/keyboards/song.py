from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from loader import _


class SongCallback(CallbackData, prefix="song"):
    data: str
    id: int
    action: str


def get_song_markup(data: str, id: int, chords: bool = False, library: bool = False, inline: bool = False):
    markup = InlineKeyboardBuilder()

    markup.add(
        InlineKeyboardButton(
            text=_("Chords: {}").format(chords),
            callback_data=SongCallback(data=data, id=id, action=f"chords_{not chords}").pack(),
        )
    )
    if not inline:
        markup.add(
            InlineKeyboardButton(text=_("Music"), callback_data=SongCallback(data=data, id=id, action="music").pack())
        )
        markup.row(
            InlineKeyboardButton(
                text=_("In library: {}").format(library),
                callback_data=SongCallback(data=data, id=id, action=f"library_{not library}").pack()
            )
        )
        markup.row(
            InlineKeyboardButton(
                text=_("Back"), callback_data=SongCallback(data=data, id=id, action="back").pack()
            )
        )

    return markup.as_markup()
