from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.spy_game.single_device.view_role import SingleDeviceSpyGameViewRoleAction


def single_device_spy_game_view_role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("play-single-device-spy-game-prepare.button-view-role"),
                    callback_data=SingleDeviceSpyGameViewRoleAction().pack()
                )
            ]
        ]
    )
