from typing import Dict

from aiogram.utils.i18n import lazy_gettext as __
from babel.support import LazyProxy

from app.enums.player_role import PlayerRole


class DictFactory:
    @staticmethod
    def single_device_role_message() -> Dict[PlayerRole, LazyProxy]:
        return {
            PlayerRole.CITIZEN: __("message.single_device.play.view_role.citizen"),
            PlayerRole.SPY: __("message.single_device.play.view_role.spy")
        }

