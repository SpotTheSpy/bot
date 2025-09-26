import asyncio
from asyncio import Task
from typing import Dict, Any, Never, List, Tuple
from uuid import UUID

from aiogram import Bot
from aiogram.enums import MessageEntityType
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message, MessageEntity, User as AiogramUser
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.menu import MenuAction
from app.actions.multi_device_leave import MultiDeviceLeaveAction
from app.actions.multi_device_start import MultiDeviceStartAction
from app.controllers.multi_device_games import MultiDeviceGamesController
from app.enums.payload_type import PayloadType
from app.exceptions.already_in_game import AlreadyInGameError
from app.exceptions.game_has_already_started import GameHasAlreadyStartedError
from app.exceptions.invalid_player_amount import InvalidPlayerAmountError
from app.exceptions.not_found import NotFoundError
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.multi_device_game import MultiDeviceGame
from app.models.user import User
from app.parameters import Parameters
from app.scenes.base import BaseScene


class MultiDevicePlayScene(BaseScene, state="multi_device_play"):
    _UPDATE_TASKS: Dict[UUID, Task] = {}
    _RECRUIT_MESSAGES: Dict[UUID, Dict[UUID, Message]] = {}

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game_json: Dict[str, Any] = await state.get_value("game")

        if game_json is None:
            return

        game = MultiDeviceGame.from_json(game_json)
        await state.update_data(game=game.to_json())

        messages: Dict[UUID, Message] = {user.id: callback_query.message}

        #  noinspection PyUnreachableCode
        task: Task = asyncio.create_task(
            self._always_update_recruitment(
                messages,
                callback_query.bot,
                game.game_id,
                state,
                multi_device_games
            )
        )

        self._UPDATE_TASKS[game.game_id] = task
        self._RECRUIT_MESSAGES[game.game_id] = messages

        text, entities = await self._create_recruitment_message(game, callback_query.bot)

        await self.edit_message(
            callback_query.message,
            text,
            entities=entities,
            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(is_host=True)
        )

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            command: CommandObject,
            user: User,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        await message.delete()

        payload: str = command.args

        if not payload.startswith(PayloadType.JOIN):
            return

        try:
            game_id = UUID(payload.split(":")[1])
        except (ValueError, IndexError):
            return

        try:
            game: MultiDeviceGame = await multi_device_games.join_game(
                game_id,
                user.id
            )
        except NotFoundError:
            await message.answer(_("message.multi_device.recruit.game_not_found"))
            return
        except GameHasAlreadyStartedError:
            await message.answer(_("message.multi_device.recruit.game_has_already_started"))
            return
        except AlreadyInGameError:
            await message.answer(_("message.multi_device.recruit.already_in_game"))
            return
        except InvalidPlayerAmountError:
            await message.answer(_("message.multi_device.recruit.too_many_players"))
            return

        await state.update_data(game=game.to_json())

        text, entities = await self._create_recruitment_message(game, message.bot)

        new_message: Message = await message.answer(
            text,
            entities=entities,
            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard()
        )

        self._RECRUIT_MESSAGES[game.game_id][user.id] = new_message

    @on.callback_query(MultiDeviceStartAction.filter())
    async def on_start(
            self,
            callback_query: CallbackQuery,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game_json: Dict[str, Any] = await state.get_value("game")

        if game_json is None:
            return

        try:
            game: MultiDeviceGame = await multi_device_games.start(UUID(game_json.get("game_id")))
        except InvalidPlayerAmountError:
            await callback_query.answer(_("answer.multi_device.too_few_players"))
            return
        except (ValueError, KeyError, NotFoundError):
            return

        text, entities = await self._create_recruitment_message(game, callback_query.bot)

        await self.edit_message(
            callback_query.message,
            text,
            entities=entities,
            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(is_host=True)
        )

    @on.callback_query(MultiDeviceLeaveAction.filter())
    async def on_leave(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game_json: Dict[str, Any] = await state.get_value("game")

        if game_json is None:
            return

        try:
            game_id = UUID(game_json.get("game_id"))
        except (ValueError, KeyError):
            return

        await multi_device_games.leave_game(
            game_id,
            user.id
        )

        messages: Dict[UUID, Message] = self._RECRUIT_MESSAGES[game_id]
        if user.id in messages:
            messages.pop(user.id)

        await state.clear()

        await self.edit_message(
            callback_query.message,
            _("message.multi_device.leave")
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
            messages: Dict[UUID, Message],
            bot: Bot,
            game_id: UUID,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> Never:
        while True:
            if not messages:
                return

            await asyncio.sleep(Parameters.API_POLLING_TIMEOUT)

            game: MultiDeviceGame = await multi_device_games.get_game(game_id)
            await state.update_data(game=game.to_json())
            text, entities = await self._create_recruitment_message(game, bot)

            for message in messages.values():
                await self.edit_message(
                    message,
                    text,
                    entities=entities,
                    reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(message[0] == game.host_id)
                )

    @staticmethod
    async def _create_recruitment_message(
            game: MultiDeviceGame,
            bot: Bot
    ) -> Tuple[str, List[MessageEntity]]:
        player_strings: List[str] = []

        for index, player in enumerate(game.players):
            if player.user_id == game.host_id:
                player_strings.append(f"{index + 1}. {player.first_name} (Host)")
            else:
                player_strings.append(f"{index + 1}. {player.first_name}")

        text: str = f"""
        new game\n\njoin\n\n{"\n".join(player_strings)}\n\nPlayers: {len(game.players)}/{game.player_amount}
        """

        entities: List[MessageEntity] = [
            MessageEntity(
                type=MessageEntityType.TEXT_LINK,
                url=await create_start_link(bot, f"{PayloadType.JOIN}:{game.game_id}", encode=True),
                offset=text.find("join"),
                length=4
            )
        ]

        for player, player_string in zip(game.players, player_strings):
            entities.append(
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
            )

        return text, entities
