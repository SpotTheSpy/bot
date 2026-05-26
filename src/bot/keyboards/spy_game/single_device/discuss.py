from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.spy_game.single_device.finish import SingleDeviceSpyGameFinishAction


def single_device_spy_game_discuss_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("play-single-device-spy-game-discuss.button-finish"),
                    callback_data=SingleDeviceSpyGameFinishAction().pack()
                )
            ]
        ]
    )
