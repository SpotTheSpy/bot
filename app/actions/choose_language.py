from app.actions.action import Action
from app.enums.locale import Locale


class ChooseLanguageAction(Action, prefix="choose_language"):
    """
    Callback action for choosing a new language.
    """

    language_type: Locale
