import asyncio
from asyncio import Task
from typing import Dict, Any, Never, List, Tuple
from uuid import UUID

from aiogram.enums import MessageEntityType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message, MessageEntity, User as AiogramUser

from app.actions.back import BackAction
from app.actions.menu import MenuAction
from app.controllers.multi_device_games import MultiDeviceGamesController
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.multi_device_game import MultiDeviceGame
from app.models.user import User
from app.parameters import Parameters
from app.scenes.base import BaseScene


class MultiDeviceRecruitScene(BaseScene, state="multi_device_recruit"):
    _UPDATE_TASKS: Dict[UUID, Task] = {}
    _RECRUIT_MESSAGES: Dict[UUID, List[Message]] = {}

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game_json: Dict[str, Any] = await state.get_value("game")

        if game_json is None:
            return

        game = MultiDeviceGame.from_json(game_json)

        messages: List[Message] = [callback_query.message]

        #  noinspection PyUnreachableCode
        task: Task = asyncio.create_task(
            self._always_update_recruitment(
                messages,
                game.game_id,
                state,
                multi_device_games
            )
        )

        self._UPDATE_TASKS[game.game_id] = task
        self._GAME_MESSAGES[game.game_id] = messages

        text, entities = self._create_recruitment_message(game)

        await self.edit_message(
            message,
            text,
            entities=entities,
            reply_markup=InlineKeyboardFactory.back_keyboard()
        )

    @on.callback_query(MenuAction.filter())
    async def on_menu(
            self,
            callback_query: CallbackQuery,
            user: User
    ) -> None:
        await callback_query.answer()
        await self.wizard.goto("start", user=user)

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.wizard.back()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()

    async def _always_update_recruitment(
            self,
            messages: List[Message],
            game_id: UUID,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> Never:
        while True:
            await asyncio.sleep(Parameters.API_POLLING_TIMEOUT)

            game: MultiDeviceGame = await multi_device_games.get_game(game_id)
            await state.update_data(game=game.to_json())

            text, entities = self._create_recruitment_message(game)

            for message in messages:
                await self.edit_message(
                    message,
                    text,
                    entities=entities,
                    reply_markup=InlineKeyboardFactory.back_keyboard()
                )

    @staticmethod
    def _create_recruitment_message(game: MultiDeviceGame) -> Tuple[str, List[MessageEntity]]:
        player_strings: List[str] = []

        for index, player in enumerate(game.players):
            if player.user_id == game.host_id:
                player_strings.append(f"{index + 1}. {player.first_name} ★")
            else:
                player_strings.append(f"{index + 1}. {player.first_name}")

        text: str = f"""
        new game\n\n{"\n".join(player_strings)}\n\nPlayers: {len(game.players)}/{game.player_amount}
        """

        entities: List[MessageEntity] = [
            MessageEntity(
                type=MessageEntityType.TEXT_MENTION,
                user=AiogramUser(
                    id=player.telegram_id,
                    first_name=player.first_name,
                    is_bot=False
                ),
                offset=text.find(player_string),
                length=len(player_string)
            )
            for player, player_string in zip(game.players, player_strings)
        ]

        return text, entities
