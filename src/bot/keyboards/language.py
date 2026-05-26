from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import LazyProxy
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.actions.back import BackAction
from src.bot.actions.switch_language import SwitchLanguageAction
from src.core.enums.locale import Locale


def language_keyboard(translation_locale: str | None = None) -> InlineKeyboardMarkup:
    """
    Create a keyboard for selecting desired language.

    :param translation_locale: Locale for translating button text.
    :return: InlineKeyboardMarkup.
    """

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for locale in Locale:
        locale = Locale(locale)

        builder.row(
            InlineKeyboardButton(
                text=LazyProxy(
                    "language.button-select",
                    translation_locale,
                    select_locale=locale,
                ),
                callback_data=SwitchLanguageAction(locale=locale).pack()
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=LazyProxy(
                "button-back",
                translation_locale,
            ),
            callback_data=BackAction().pack(),
        )
    )

    return builder.as_markup()
