
from aiogram_i18n import I18nContext, LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.switch_scene import SwitchSceneAction


def greeting_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy("greeting.button-language"),
                    callback_data=SwitchSceneAction(scene="language").pack(),
                )
            ]
        ]
    )
