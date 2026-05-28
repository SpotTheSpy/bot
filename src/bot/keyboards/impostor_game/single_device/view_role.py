from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.impostor_game.single_device.view_question import SingleDeviceImpostorGameViewQuestionAction


def single_device_impostor_game_view_question_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("play-single-device-impostor-game-prepare.button-view-question"),
                    callback_data=SingleDeviceImpostorGameViewQuestionAction().pack()
                )
            ]
        ]
    )
