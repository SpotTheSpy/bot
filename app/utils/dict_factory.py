from json import loads
from typing import Dict

from aiogram.utils.i18n import lazy_gettext as __
from babel.support import LazyProxy

from app.enums.player_role import PlayerRole


class DictFactory:
    single_device_role_messages: Dict[PlayerRole, LazyProxy] = {
        PlayerRole.CITIZEN: __("message.single_device.play.view_role.citizen"),
        PlayerRole.SPY: __("message.single_device.play.view_role.spy")
    }

    multi_device_role_messages: Dict[PlayerRole, LazyProxy] = {
        PlayerRole.CITIZEN: __("message.multi_device.play.view_role.citizen"),
        PlayerRole.SPY: __("message.multi_device.play.view_role.spy")
    }

    secret_words: LazyProxy = __("data.secret_words")

    @classmethod
    def get_secret_word(
            cls,
            secret_word: str
    ) -> str:
        return loads(str(cls.secret_words)).get(secret_word, secret_word)
