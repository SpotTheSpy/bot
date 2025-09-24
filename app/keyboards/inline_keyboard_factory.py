from typing import List, Set

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.finish import FinishAction
from app.actions.menu import MenuAction
from app.actions.next_player import NextPlayerAction
from app.actions.page_turn import PageTurnAction
from app.actions.play import PlayAction
from app.actions.settings import SettingsAction
from app.actions.start import StartSingleDeviceAction
from app.actions.view_role import ViewRoleAction
from app.enums.game_style import GameStyle
from app.enums.page_turn import PageTurn


class InlineKeyboardFactory:
    @staticmethod
    def menu_button() -> InlineKeyboardButton:
        return InlineKeyboardButton(text=_("button.menu"), callback_data=MenuAction().pack())

    @staticmethod
    def back_button() -> InlineKeyboardButton:
        return InlineKeyboardButton(text=_("button.back"), callback_data=BackAction().pack())

    @staticmethod
    def pagination_button(
            page_turn: PageTurn
    ) -> InlineKeyboardButton:
        button_text: str = {
            PageTurn.RIGHT: _("button.right"),
            PageTurn.LEFT: _("button.left")
        }.get(page_turn)

        return InlineKeyboardButton(text=button_text, callback_data=PageTurnAction(turn=page_turn).pack())

    @classmethod
    def menu_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[cls.menu_button()]])

    @classmethod
    def back_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[cls.back_button()]])

    @classmethod
    def pagination_row(
            cls,
            *,
            exclude_turns: Set[PageTurn] | None = None
    ) -> List[InlineKeyboardButton]:
        return [
            cls.pagination_button(page_turn) for page_turn in [PageTurn.LEFT, PageTurn.RIGHT]
            if page_turn not in exclude_turns
        ]

    @staticmethod
    def start_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.start.play_single_device"),
                        callback_data=PlayAction(style=GameStyle.SINGLE_DEVICE).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_("button.start.play_multi_device"),
                        callback_data=PlayAction(style=GameStyle.MULTI_DEVICE).pack()
                    )
                ]
            ]
        )

    @classmethod
    def single_device_settings_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=_("button.got_it"), callback_data=SettingsAction().pack())
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_play_keyboard(
            cls,
            *,
            exclude_turns: Set[PageTurn] | None = None
    ) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                cls.pagination_row(exclude_turns=exclude_turns),
                [
                    InlineKeyboardButton(
                        text=_("button.single_device.play"),
                        callback_data=StartSingleDeviceAction().pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_view_role_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.single_device.view_role"),
                        callback_data=ViewRoleAction().pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_next_player_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.single_device.next_player"),
                        callback_data=NextPlayerAction().pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_finish_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=_("button.single_device.finish"), callback_data=FinishAction().pack())
                ],
                [
                    cls.back_button()
                ]
            ]
        )
