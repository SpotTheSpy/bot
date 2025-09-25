from app.actions.action import Action
from app.enums.language_type import LanguageType


class ChooseLanguageAction(Action, prefix="choose_language"):
    language_type: LanguageType
