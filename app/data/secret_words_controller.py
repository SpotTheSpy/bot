from json import loads

from aiogram.utils.i18n import gettext as _


class SecretWordsController:
    @staticmethod
    def get_secret_word(
            secret_word: str,
            *,
            locale: str | None = None
    ) -> str:
        return loads(_("data.secret_words", locale=locale)).get(secret_word, secret_word)
