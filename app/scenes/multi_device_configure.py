from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.multi_device_choose_player_amount import MultiDeviceChoosePlayerAmountAction
from app.actions.multi_device_play import MultiDevicePlayAction
from app.models.bot_user import BotUser
from app.models.user import User
from app.parameters import Parameters
from app.scenes.base import BaseScene
from app.utils.inline_keyboard_factory import InlineKeyboardFactory


class MultiDeviceConfigureScene(BaseScene, state="multi_device_configure"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            state: FSMContext,
            player_amount: int | None = None
    ) -> None:
        if player_amount is None:
            player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT

        await state.update_data(player_amount=player_amount)

        await callback_query.answer()
        await user.edit_message(
            text=_("message.multi_device.configure"),
            reply_markup=InlineKeyboardFactory.multi_device_configure_keyboard(
                min_amount=Parameters.MIN_PLAYER_AMOUNT,
                max_amount=Parameters.MAX_PLAYER_AMOUNT,
                selected_amount=player_amount
            )
        )

    @on.callback_query(MultiDeviceChoosePlayerAmountAction.filter())
    async def on_choose_player_amount(
            self,
            callback_query: CallbackQuery,
            callback_data: MultiDeviceChoosePlayerAmountAction,
            user: BotUser,
            state: FSMContext
    ) -> None:
        await state.update_data(player_amount=callback_data.player_amount)

        await callback_query.answer()
        await user.edit_message(
            text=_("message.multi_device.configure"),
            reply_markup=InlineKeyboardFactory.multi_device_configure_keyboard(
                min_amount=Parameters.MIN_PLAYER_AMOUNT,
                max_amount=Parameters.MAX_PLAYER_AMOUNT,
                selected_amount=callback_data.player_amount
            )
        )

    @on.callback_query(MultiDevicePlayAction.filter())
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
            "multi_device_play",
            user=user,
            player_amount=player_amount
        )

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
