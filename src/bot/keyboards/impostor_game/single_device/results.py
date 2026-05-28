from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.back import BackAction
from src.bot.actions.impostor_game.single_device.play_again import SingleDeviceImpostorGamePlayAgainAction


def single_device_impostor_game_results_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("play-single-device-impostor-game-results.button-play-again"),
                    callback_data=SingleDeviceImpostorGamePlayAgainAction().pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy("button-back"),
                    callback_data=BackAction().pack()
                )
            ],
        ]
    )
