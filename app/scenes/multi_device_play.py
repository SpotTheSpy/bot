from uuid import UUID

from aiogram.filters import CommandObject
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message

from app.actions.multi_device_finish import MultiDeviceFinishAction
from app.actions.multi_device_leave import MultiDeviceLeaveAction
from app.actions.multi_device_play_again import MultiDevicePlayAgainAction
from app.actions.multi_device_start import MultiDeviceStartAction
from app.controllers.multi_device_games import MultiDeviceGamesController
from app.enums.payload import Payload
from app.models.bot_user import BotUser
from app.models.multi_device_game import MultiDeviceGame
from app.models.user import User
from app.scenes.base import BaseScene


class MultiDevicePlayScene(BaseScene, state="multi_device_play"):
    """
    Scene for playing a multi-device game.
    """

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            player_amount: int
    ) -> None:
        await user.recruit_multi_device_game(player_amount=player_amount)
        await callback_query.answer()

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            command: CommandObject,
            user: BotUser
    ) -> None:
        payload: str = command.args

        if not payload.startswith(Payload.JOIN):
            await message.delete()
            return

        try:
            game_id = UUID(payload.split(":")[1])
        except (ValueError, IndexError):
            await message.delete()
            return

        await user.join_multi_device_game(game_id=game_id)
        await message.delete()

    @on.callback_query(MultiDeviceStartAction.filter())
    async def on_start(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.start_multi_device_game()
        await callback_query.answer()

    @on.callback_query(MultiDeviceFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.finish_multi_device_game()
        await callback_query.answer()

    @on.callback_query(MultiDevicePlayAgainAction.filter())
    async def on_play_again(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.restart_multi_device_game()
        await callback_query.answer()

    @on.callback_query(MultiDeviceLeaveAction.filter())
    async def on_leave(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.leave()

    async def on_scene_leave(
            self,
            user: BotUser
    ) -> None:
        await user.leave_multi_device_game()

    async def on_back(
            self,
            user: User,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)

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
