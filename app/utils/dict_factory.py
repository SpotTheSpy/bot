from json import loads
from typing import Dict

from aiogram.utils.i18n import lazy_gettext as __
from babel.support import LazyProxy

from app.enums.player_role import PlayerRole


class DictFactory:
    """
    Global class for all mapping objects.
    """

    # Mapping for player role and role message in a single-device game.
    single_device_role_messages: Dict[PlayerRole, LazyProxy] = {
        PlayerRole.CITIZEN: __("message.single_device.play.view_role.citizen"),
        PlayerRole.SPY: __("message.single_device.play.view_role.spy")
    }

    # Mapping for player role and role message in a multi-device game.
    multi_device_role_messages: Dict[PlayerRole, LazyProxy] = {
        PlayerRole.CITIZEN: __("message.multi_device.play.view_role.citizen"),
        PlayerRole.SPY: __("message.multi_device.play.view_role.spy")
    }

    # Mapping of secret words as a string
    secret_words: LazyProxy = __("data.secret_words")

    @classmethod
    def get_secret_word(
            cls,
            secret_word: str
    ) -> str:
        """
        Retrieve a secret word translation from a secret word tag.

        :param secret_word: Secret word tag.
        :return: Translation of a secret word.
        """

        return loads(str(cls.secret_words)).get(secret_word, secret_word)
