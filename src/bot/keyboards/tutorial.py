from aiogram.types import InlineKeyboardMarkup
from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardButton

from src.bot.actions.back import BackAction
from src.bot.actions.switch_scene import SwitchSceneAction


def tutorial_keyboard(
        next_scene: str,
) -> InlineKeyboardMarkup:
    """
    Create a keyboard for any tutorial message.

    :param next_scene: State for the next scene.
    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("button-got-it"),
                    callback_data=SwitchSceneAction(scene=next_scene).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy("button-back"),
                    callback_data=BackAction().pack(),
                )
            ],
        ]
    )
