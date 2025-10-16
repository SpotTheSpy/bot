from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.actions.back import BackAction
from app.actions.choose_language import ChooseLanguageAction
from app.actions.menu import MenuAction
from app.actions.multi_device_choose_player_amount import MultiDeviceChoosePlayerAmountAction
from app.actions.multi_device_finish import MultiDeviceFinishAction
from app.actions.multi_device_leave import MultiDeviceLeaveAction
from app.actions.multi_device_play import MultiDevicePlayAction
from app.actions.multi_device_play_again import MultiDevicePlayAgainAction
from app.actions.multi_device_start import MultiDeviceStartAction
from app.actions.single_device_choose_player_amount import SingleDeviceChoosePlayerAmountAction
from app.actions.single_device_finish import SingleDeviceFinishAction
from app.actions.single_device_play import SingleDevicePlayAction
from app.actions.single_device_play_again import SingleDevicePlayAgainAction
from app.actions.single_device_proceed import SingleDeviceProceedPlayerAction
from app.actions.single_device_view_role import SingleDeviceViewRoleAction
from app.actions.switch_scene import SwitchSceneAction
from app.enums.locale import Locale


class KeyboardFactory:
    """
    Class for generating all variants of keyboards.
    """

    @staticmethod
    def menu_button() -> InlineKeyboardButton:
        """
        :return: Menu button instance.
        """

        return InlineKeyboardButton(text=_("button.menu"), callback_data=MenuAction().pack())

    @staticmethod
    def back_button() -> InlineKeyboardButton:
        """
        :return: Back button instance.
        """

        return InlineKeyboardButton(text=_("button.back"), callback_data=BackAction().pack())

    @classmethod
    def menu_keyboard(cls) -> InlineKeyboardMarkup:
        """
        :return: Menu inline keyboard instance.
        """

        return InlineKeyboardMarkup(inline_keyboard=[[cls.menu_button()]])

    @classmethod
    def back_keyboard(cls) -> InlineKeyboardMarkup:
        """
        :return: Back inline keyboard instance.
        """

        return InlineKeyboardMarkup(inline_keyboard=[[cls.back_button()]])

    @staticmethod
    def start_keyboard(locale: str | None = None) -> InlineKeyboardMarkup:
        """
        :param locale: Locale for translating message. If None, a context locale is used.
        :return: Start inline keyboard instance.
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.start.play", locale=locale),
                        callback_data=SwitchSceneAction(scene="choose_device").pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_("button.start.language", locale=locale),
                        callback_data=SwitchSceneAction(scene="language").pack()
                    )
                ]
            ]
        )

    @classmethod
    def choose_device_keyboard(cls) -> InlineKeyboardMarkup:
        """
        :return: Choose device inline keyboard instance.
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.choose_device.single_device"),
                        callback_data=SwitchSceneAction(scene="single_device_explain").pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_("button.choose_device.multi_device"),
                        callback_data=SwitchSceneAction(scene="multi_device_explain").pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def choose_language_keyboard(cls) -> InlineKeyboardMarkup:
        """
        :return: Choose language inline keyboard instance.
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.language.en"),
                        callback_data=ChooseLanguageAction(locale=Locale.ENGLISH).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_("button.language.uk"),
                        callback_data=ChooseLanguageAction(locale=Locale.UKRAINIAN).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_("button.language.ru"),
                        callback_data=ChooseLanguageAction(locale=Locale.RUSSIAN).pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_explain_keyboard(cls) -> InlineKeyboardMarkup:
        """
        :return: Single-device explain keyboard instance.
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.got_it"),
                        callback_data=SwitchSceneAction(scene="single_device_configure").pack()
                    )
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
            min_amount: int,
            max_amount: int,
            selected_amount: int | None = None
    ) -> InlineKeyboardMarkup:
        """
        :param min_amount: Minimum possible amount of players.
        :param max_amount: Maximum possible amount of players.
        :param selected_amount: Selected amount of players.
        :return: Single-device configure keyboard instance.
        """

        builder = InlineKeyboardBuilder()

        for player_amount in range(min_amount, max_amount + 1):
            if player_amount == selected_amount:
                button_text: str = _("button.single_device.configure.player_amount.selected").format(
                    player_amount=player_amount
                )
            else:
                button_text: str = _("button.single_device.configure.player_amount").format(
                    player_amount=player_amount
                )

            builder.button(
                text=button_text,
                callback_data=SingleDeviceChoosePlayerAmountAction(player_amount=player_amount).pack()
            )

        builder.adjust(3, repeat=True)

        builder.row(
            InlineKeyboardButton(
                text=_("button.single_device.play"),
                callback_data=SingleDevicePlayAction().pack()
            )
        )
        builder.row(cls.back_button())

        return builder.as_markup()

    @classmethod
    def single_device_view_role_keyboard(cls) -> InlineKeyboardMarkup:
        """
        :return: Single-device view role inline keyboard instance.
        """

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
        """
        :return: Single-device proceed inline keyboard instance.
        """

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
        """
        :return: Single-device finish inline keyboard instance.
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.single_device.finish"),
                        callback_data=SingleDeviceFinishAction().pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def single_device_play_again_keyboard(cls) -> InlineKeyboardMarkup:
        """
        :return: Single-device play again inline keyboard instance.
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.single_device.play_again"),
                        callback_data=SingleDevicePlayAgainAction().pack()
                    )
                ],
                [
                    cls.menu_button()
                ]
            ]
        )

    @classmethod
    def multi_device_explain_keyboard(cls) -> InlineKeyboardMarkup:
        """
        :return: Multi-device explain keyboard instance.
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.got_it"),
                        callback_data=SwitchSceneAction(scene="multi_device_configure").pack()
                    )
                ],
                [
                    cls.back_button()
                ]
            ]
        )

    @classmethod
    def multi_device_configure_keyboard(
            cls,
            *,
            min_amount: int,
            max_amount: int,
            selected_amount: int | None = None
    ) -> InlineKeyboardMarkup:
        """
        :param min_amount: Minimum possible amount of players.
        :param max_amount: Maximum possible amount of players.
        :param selected_amount: Selected amount of players.
        :return: Multi-device configure keyboard instance.
        """

        builder = InlineKeyboardBuilder()

        for player_amount in range(min_amount, max_amount + 1):
            if player_amount == selected_amount:
                button_text: str = _("button.multi_device.configure.player_amount.selected").format(
                    player_amount=player_amount
                )
            else:
                button_text: str = _("button.multi_device.configure.player_amount").format(
                    player_amount=player_amount
                )

            builder.button(
                text=button_text,
                callback_data=MultiDeviceChoosePlayerAmountAction(player_amount=player_amount).pack()
            )

        builder.adjust(3, repeat=True)

        builder.row(
            InlineKeyboardButton(
                text=_("button.multi_device.play"),
                callback_data=MultiDevicePlayAction().pack()
            )
        )
        builder.row(cls.back_button())

        return builder.as_markup()

    @classmethod
    def multi_device_recruit_keyboard(
            cls,
            *,
            is_host: bool = False
    ) -> InlineKeyboardMarkup:
        """
        :param is_host: Whether to show inline keyboard for host player.
        :return: Multi-device recruit keyboard instance.
        """

        if is_host:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_("button.multi_device.start"),
                            callback_data=MultiDeviceStartAction().pack()
                        )
                    ],
                    [
                        cls.back_button()
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_("button.multi_device.leave"),
                            callback_data=MultiDeviceLeaveAction().pack()
                        )
                    ]
                ]
            )

    @classmethod
    def multi_device_view_role_keyboard(
            cls,
            *,
            is_host: bool = False
    ) -> InlineKeyboardMarkup | None:
        """
        :param is_host: Whether to show inline keyboard for host player.
        :return: Multi-device view role inline keyboard instance.
        """

        if not is_host:
            return

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.multi_device.finish"),
                        callback_data=MultiDeviceFinishAction().pack()
                    )
                ]
            ]
        )

    @classmethod
    def multi_device_play_again_keyboard(
            cls,
            *,
            is_host: bool = False
    ) -> InlineKeyboardMarkup:
        """
        :param is_host: Whether to show inline keyboard for host player.
        :return: Multi-device play again inline keyboard instance.
        """

        if not is_host:
            return cls.menu_keyboard()

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("button.multi_device.play_again"),
                        callback_data=MultiDevicePlayAgainAction().pack()
                    )
                ],
                [
                    cls.menu_button()
                ]
            ]
        )
