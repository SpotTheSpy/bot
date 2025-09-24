from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.finish import FinishAction
from app.actions.next_player import NextPlayerAction
from app.actions.play import PlayAction
from app.actions.start import StartSingleDeviceAction, StartMultiDeviceAction
from app.actions.view_role import ViewRoleAction
from app.enums.game_style import GameStyle


class InlineKeyboardFactory:
    @staticmethod
    def back_button() -> InlineKeyboardButton:
        return InlineKeyboardButton(text=_("button.back"), callback_data=BackAction().pack())

    @classmethod
    def back_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[cls.back_button()]])

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
    def play_keyboard(
            cls,
            style: GameStyle
    ) -> InlineKeyboardMarkup:
        callback_data: str = {
            GameStyle.SINGLE_DEVICE: StartSingleDeviceAction(),
            GameStyle.MULTI_DEVICE: StartMultiDeviceAction()
        }.get(style).pack()

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=_("button.single_device.play"), callback_data=callback_data)
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
