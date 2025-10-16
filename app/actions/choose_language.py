from app.actions.action import Action
from app.enums.locale import Locale


class ChooseLanguageAction(Action, prefix="choose_language"):
    """
    Callback action for choosing a new language.

    Attributes:
        locale: New locale to be set.
    """

    locale: Locale
    """
    New locale to be set.
    """
