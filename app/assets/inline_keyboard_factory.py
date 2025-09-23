from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from app.actions.play import PlayAction
from app.enums.game_style import GameStyle


class InlineKeyboardFactory:
    @staticmethod
    def create_start_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.start.play_single_device"),
                        callback_data=PlayAction(style=GameStyle.SINGLE_DEVICE).pack()
                    )
                ]
            ]
        )