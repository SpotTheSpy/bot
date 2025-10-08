from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message

from app.actions.single_device_finish import SingleDeviceFinishAction
from app.actions.single_device_play_again import SingleDevicePlayAgainAction
from app.actions.single_device_proceed import SingleDeviceProceedPlayerAction
from app.actions.single_device_view_role import SingleDeviceViewRoleAction
from app.models.bot_user import BotUser
from app.models.single_device_game import SingleDeviceGame
from app.scenes.base import BaseScene


class SingleDevicePlayScene(BaseScene, state="single_device_play"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            player_amount: int
    ) -> None:
        await user.start_single_device_game(player_amount=player_amount)
        await callback_query.answer()

    @on.callback_query(SingleDeviceViewRoleAction.filter())
    async def on_view_role(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.view_role_in_single_device_game()
        await callback_query.answer()

    @on.callback_query(SingleDeviceProceedPlayerAction.filter())
    async def on_proceed(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.proceed_in_single_device_game()
        await callback_query.answer()

    @on.callback_query(SingleDeviceFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.finish_single_device_game()
        await callback_query.answer()

    @on.callback_query(SingleDevicePlayAgainAction.filter())
    async def on_play_again(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.restart_single_device_game()
        await callback_query.answer()

    async def on_scene_leave(
            self,
            user: BotUser
    ) -> None:
        await user.end_single_device_game()

    async def on_back(
            self,
            user: BotUser
    ) -> None:
        game: SingleDeviceGame = await user.get_single_device_game()

        await self.wizard.back(
            user=user,
            player_amount=game.player_amount if game is not None else None
        )

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
