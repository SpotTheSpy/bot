from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.imposter_game.single_device.proceed import SingleDeviceImpostorGameProceedAction
from src.bot.actions.spy_game.single_device.proceed import SingleDeviceSpyGameProceedAction


def single_device_impostor_game_proceed_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("play-single-device-impostor-game-view-question.button-proceed"),
                    callback_data=SingleDeviceImpostorGameProceedAction().pack()
                )
            ]
        ]
    )
