from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message

from app.actions.multi_device_choose_player_amount import MultiDeviceChoosePlayerAmountAction
from app.actions.multi_device_play import MultiDevicePlayAction
from app.models.bot_user import BotUser
from app.models.user import User
from app.scenes.base import BaseScene


class MultiDeviceConfigureScene(BaseScene, state="multi_device_configure"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            player_amount: int | None = None
    ) -> None:
        await user.configure_multi_device(player_amount=player_amount)
        await callback_query.answer()

    @on.callback_query(MultiDeviceChoosePlayerAmountAction.filter())
    async def on_choose_player_amount(
            self,
            callback_query: CallbackQuery,
            callback_data: MultiDeviceChoosePlayerAmountAction,
            user: BotUser
    ) -> None:
        await user.configure_multi_device(player_amount=callback_data.player_amount)
        await callback_query.answer()

    @on.callback_query(MultiDevicePlayAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext
    ) -> None:
        player_amount: int = await state.get_value("player_amount")

        await self.wizard.goto(
            "multi_device_play",
            user=user,
            player_amount=player_amount
        )

        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
