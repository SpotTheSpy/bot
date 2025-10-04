from typing import Dict

from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from babel.support import LazyProxy

from app.enums.player_role import PlayerRole


class DictFactory:
    @staticmethod
    def single_device_role_message() -> Dict[PlayerRole, LazyProxy]:
        return {
            PlayerRole.CITIZEN: __("message.single_device.play.view_role.citizen"),
            PlayerRole.SPY: __("message.single_device.play.view_role.spy")
        }

    @staticmethod
    def multi_device_role_message(
            *,
            locale: str | None = None
    ) -> Dict[PlayerRole, str | LazyProxy]:
        if locale is not None:
            return {
                PlayerRole.CITIZEN: _("message.multi_device.play.view_role.citizen", locale=locale),
                PlayerRole.SPY: _("message.multi_device.play.view_role.spy", locale=locale)
            }

        return {
            PlayerRole.CITIZEN: __("message.multi_device.play.view_role.citizen"),
            PlayerRole.SPY: __("message.multi_device.play.view_role.spy")
        }
