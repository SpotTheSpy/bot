from json import loads
from typing import Dict, Any

from aiogram.utils.i18n import gettext as _


class SecretWordsController:
    _SECRET_WORDS: Dict[str, Any] | None = None

    @classmethod
    def get_secret_word(
            cls,
            secret_word: str
    ) -> str:
        if cls._SECRET_WORDS is None:
            cls._SECRET_WORDS = loads(_("data.secret_words"))

        return cls._SECRET_WORDS.get(secret_word, secret_word)
