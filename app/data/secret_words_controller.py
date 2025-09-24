from json import loads

from aiogram.utils.i18n import gettext as _


class SecretWordsController:
    @staticmethod
    def get_secret_word(secret_word: str) -> str:
        return loads(_("data.secret_words")).get(secret_word, secret_word)
