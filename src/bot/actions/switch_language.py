from src.bot.actions.base import BaseAction
from src.core.enums.locale import Locale


class SwitchLanguageAction(BaseAction, prefix="switch_language"):
    """
    Callback action for switching a language.
    """

    locale: Locale
    """
    New chosen locale.
    """
