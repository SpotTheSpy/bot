from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.impostor_game.single_device.finish import SingleDeviceImpostorGameFinishAction
from src.bot.actions.impostor_game.single_device.next_answer import SingleDeviceImpostorGameNextAnswerAction


def single_device_impostor_game_next_answer_keyboard(
        *,
        is_last_answer: bool = False,
) -> InlineKeyboardMarkup:
    return (
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=LazyProxy("play-single-device-impostor-game-discuss.button-next-answer"),
                        callback_data=SingleDeviceImpostorGameNextAnswerAction().pack()
                    )
                ]
            ]
        )
        if not is_last_answer
        else InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=LazyProxy("play-single-device-impostor-game-discuss.button-finish"),
                        callback_data=SingleDeviceImpostorGameFinishAction().pack()
                    )
                ]
            ]
        )
    )
