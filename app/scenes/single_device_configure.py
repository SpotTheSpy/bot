from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.single_device_choose_player_amount import SingleDeviceChoosePlayerAmountAction
from app.actions.single_device_play import SingleDevicePlayAction
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.models.user import User
from app.parameters import Parameters
from app.scenes.base import BaseScene


class SingleDeviceConfigureScene(BaseScene, state="single_device_configure"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            state: FSMContext,
            player_amount: int | None = None
    ) -> None:
        if player_amount is None:
            player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT

        await state.update_data(player_amount=player_amount)

        await callback_query.answer()
        await self.edit_message(
            callback_query.message,
            _("message.single_device.configure"),
            reply_markup=InlineKeyboardFactory.single_device_configure_keyboard(
                min_player_amount=Parameters.MIN_PLAYER_AMOUNT,
                max_player_amount=Parameters.MAX_PLAYER_AMOUNT,
                selected_player_amount=player_amount
            )
        )

    @on.callback_query(SingleDeviceChoosePlayerAmountAction.filter())
    async def on_choose_player_amount(
            self,
            callback_query: CallbackQuery,
            callback_data: SingleDeviceChoosePlayerAmountAction,
            state: FSMContext
    ) -> None:
        await state.update_data(player_amount=callback_data.player_amount)

        await callback_query.answer()
        await self.edit_message(
            callback_query.message,
            _("message.single_device.configure"),
            reply_markup=InlineKeyboardFactory.single_device_configure_keyboard(
                min_player_amount=Parameters.MIN_PLAYER_AMOUNT,
                max_player_amount=Parameters.MAX_PLAYER_AMOUNT,
                selected_player_amount=callback_data.player_amount
            )
        )

    @on.callback_query(SingleDevicePlayAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext
    ) -> None:
        player_amount: int = await state.get_value("player_amount")

        if player_amount is None:
            player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT

        await self.wizard.goto(
            "single_device_play",
            user=user,
            player_amount=player_amount
        )

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.back()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
