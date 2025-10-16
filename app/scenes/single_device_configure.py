from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message

from app.actions.single_device_choose_player_amount import SingleDeviceChoosePlayerAmountAction
from app.actions.single_device_play import SingleDevicePlayAction
from app.models.bot_user import BotUser
from app.scenes.base import BaseScene


class SingleDeviceConfigureScene(BaseScene, state="single_device_configure"):
    """
    Scene for configuring a single-device game.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            player_amount: int | None = None
    ) -> None:
        await user.configure_single_device(player_amount=player_amount)
        await callback_query.answer()

    @on.callback_query(SingleDeviceChoosePlayerAmountAction.filter())
    async def on_choose_player_amount(
            self,
            callback_query: CallbackQuery,
            callback_data: SingleDeviceChoosePlayerAmountAction,
            user: BotUser
    ) -> None:
        await user.configure_single_device(player_amount=callback_data.player_amount)
        await callback_query.answer()

    @on.callback_query(SingleDevicePlayAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            state: FSMContext
    ) -> None:
        player_amount: int = await state.get_value("player_amount")

        await self.wizard.goto(
            "single_device_play",
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
