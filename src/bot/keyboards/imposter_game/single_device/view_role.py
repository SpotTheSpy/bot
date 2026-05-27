from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.imposter_game.single_device.view_question import SingleDeviceImposterGameViewQuestionAction


def single_device_imposter_game_view_question_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("play-single-device-imposter-game-prepare.button-view-question"),
                    callback_data=SingleDeviceImposterGameViewQuestionAction().pack()
                )
            ]
        ]
    )
