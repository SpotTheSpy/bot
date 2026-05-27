
from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.switch_scene import SwitchSceneAction


def greeting_keyboard() -> InlineKeyboardMarkup:
    """
    Create a keyboard for the greeting message.

    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("greeting.button-spy-game"),
                    callback_data=SwitchSceneAction(scene="single_device_spy_game_tutorial").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy("greeting.button-impostor-game"),
                    callback_data=SwitchSceneAction(scene="single_device_impostor_game_tutorial").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy("greeting.button-language"),
                    callback_data=SwitchSceneAction(scene="language").pack(),
                )
            ],
        ]
    )
