from typing import List, Set

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.choose_device import ChooseDeviceAction
from app.actions.choose_language import ChooseLanguageAction
from app.actions.language import LanguageAction
from app.actions.single_device_finish import SingleDeviceFinishAction
from app.actions.menu import MenuAction
from app.actions.single_device_proceed import SingleDeviceProceedPlayerAction
from app.actions.page_turn import PageTurnAction
from app.actions.single_device_configure import SingleDeviceConfigureAction
from app.actions.single_device_enter import SingleDeviceEnter
from app.actions.single_device_play import SingleDevicePlayAction
from app.actions.single_device_view_role import SingleDeviceViewRoleAction
from app.enums.language_type import LanguageType
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
                        text=_("button.start.play"),
                        callback_data=ChooseDeviceAction().pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_("button.start.language"),
                        callback_data=LanguageAction().pack()
                    )
                ]
            ]
        )

    @classmethod
    def choose_device_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.choose_device.single_device"),
                        callback_data=SingleDeviceEnter().pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def choose_language_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.language.en"),
                        callback_data=ChooseLanguageAction(language_type=LanguageType.ENGLISH).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_("button.language.uk"),
                        callback_data=ChooseLanguageAction(language_type=LanguageType.UKRAINIAN).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_("button.language.ru"),
                        callback_data=ChooseLanguageAction(language_type=LanguageType.RUSSIAN).pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_explain_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=_("button.got_it"), callback_data=SingleDeviceConfigureAction().pack())
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_configure_keyboard(
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
                        callback_data=SingleDevicePlayAction().pack()
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
                        callback_data=SingleDeviceViewRoleAction().pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_proceed_keyboard(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.single_device.proceed"),
                        callback_data=SingleDeviceProceedPlayerAction().pack()
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
                    InlineKeyboardButton(text=_("button.single_device.finish"), callback_data=SingleDeviceFinishAction().pack())
                ],
                [
                    cls.back_button()
                ]
            ]
        )
