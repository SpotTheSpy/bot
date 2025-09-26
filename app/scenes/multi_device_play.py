import asyncio
from asyncio import Task
from typing import Dict, Any, List, Tuple, Never
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
from app.actions.multi_device_finish import MultiDeviceFinishAction
from app.actions.multi_device_leave import MultiDeviceLeaveAction
from app.actions.multi_device_start import MultiDeviceStartAction
from app.controllers.multi_device_games import MultiDeviceGamesController
from app.data.secret_words_controller import SecretWordsController
from app.enums.payload_type import PayloadType
from app.enums.player_role import PlayerRole
from app.exceptions.already_in_game import AlreadyInGameError
from app.exceptions.game_has_already_started import GameHasAlreadyStartedError
from app.exceptions.invalid_player_amount import InvalidPlayerAmountError
from app.exceptions.not_found import NotFoundError
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.multi_device_game import MultiDeviceGame, MultiDevicePlayer
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
            await message.answer(_("message.multi_device.play.recruit.game_not_found"))
            return
        except GameHasAlreadyStartedError:
            await message.answer(_("message.multi_device.play.recruit.game_has_already_started"))
            return
        except AlreadyInGameError:
            await message.answer(_("message.multi_device.play.recruit.already_in_game"))
            return
        except InvalidPlayerAmountError:
            await message.answer(_("message.multi_device.play.recruit.too_many_players"))
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
            user: User,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game_json: Dict[str, Any] = await state.get_value("game")

        if game_json is None:
            return

        try:
            game: MultiDeviceGame = await multi_device_games.start(UUID(game_json.get("game_id")))
        except InvalidPlayerAmountError:
            await callback_query.answer(_("answer.multi_device.play.too_few_players"))
            return
        except (ValueError, KeyError, NotFoundError):
            return

        await state.update_data(game=game.to_json())

        self._UPDATE_TASKS[game.game_id].cancel()
        self._UPDATE_TASKS.pop(game.game_id)

        players: Dict[UUID, MultiDevicePlayer] = {player.user_id: player for player in game.players}

        for user_id, message in self._RECRUIT_MESSAGES[game.game_id].items():
            role: PlayerRole = players[user_id].role

            if role is None:
                return

            message_text: str = {
                PlayerRole.CITIZEN: _("message.multi_device.play.view_role.citizen"),
                PlayerRole.SPY: _("message.multi_device.play.view_role.spy")
            }.get(role)

            await self.edit_message(
                message,
                message_text.format(
                    secret_word=SecretWordsController.get_secret_word(game.secret_word)
                ),
                reply_markup=InlineKeyboardFactory.multi_device_view_role_keyboard(
                    is_host=user_id == game.host_id
                )
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

        game_id = UUID(game_json.get("game_id"))

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
            _("message.multi_device.play.leave")
        )

        await self.wizard.exit()

    @on.callback_query(MultiDeviceFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            state: FSMContext
    ) -> None:
        game_json: Dict[str, Any] = await state.get_value("game")

        if game_json is None:
            return

        game = MultiDeviceGame.from_json(game_json)

        try:
            spy: MultiDevicePlayer = [player for player in game.players if player.role == PlayerRole.SPY][0]
        except IndexError:
            return

        for message in self._RECRUIT_MESSAGES[game.game_id].values():
            await self.edit_message(
                message,
                _("message.multi_device.play.finish").format(
                    secret_word=SecretWordsController.get_secret_word(game.secret_word),
                    first_name=spy.first_name
                ),
                reply_markup=InlineKeyboardFactory.menu_keyboard()
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

            for user_id, message in messages.items():
                await self.edit_message(
                    message,
                    text,
                    entities=entities,
                    reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                        is_host=user_id == game.host_id
                    )
                )

    @classmethod
    async def _create_recruitment_message(
            cls,
            game: MultiDeviceGame,
            bot: Bot
    ) -> Tuple[str, List[MessageEntity]]:
        players: List[str] = []

        for index, player in enumerate(game.players):
            if player.user_id == game.host_id:
                players.append(
                    _("message.multi_device.play.recruit.player.host").format(
                        index=index + 1,
                        first_name=player.first_name
                    )
                )
            else:
                players.append(
                    _("message.multi_device.play.recruit.player").format(
                        index=index + 1,
                        first_name=player.first_name
                    )
                )

        return cls._get_entities(
            _("message.multi_device.play.recruit").format(
                players="\n".join(players),
                player_amount=len(game.players),
                max_player_amount=game.player_amount
            ),
            await create_start_link(bot, f"{PayloadType.JOIN}:{game.game_id}", encode=True),
            game.players
        )

    @staticmethod
    def _get_entities(
            text: str,
            join_url: str,
            players: List[MultiDevicePlayer]
    ) -> Tuple[str, List[MessageEntity]]:
        entities: List[MessageEntity] = []
        tags_to_find: List[str] = ["b", "join", "player"]

        player_index: int = 0

        while True:
            indices: List[int] = [text.find(f"<{tag}>") for tag in tags_to_find]

            closest_tag_index: int = -1
            for index in indices:
                if index == -1:
                    continue
                if closest_tag_index == -1 or index < closest_tag_index:
                    closest_tag_index = index

            if closest_tag_index == -1:
                break

            tag: str = tags_to_find[indices.index(closest_tag_index)]
            open_tag: str = f"<{tag}>"
            close_tag: str = f"</{tag}>"

            open_tag_index: int = text.find(open_tag)
            close_tag_index: int = text.find(close_tag)

            match tag:
                case "b":
                    entities.append(
                        MessageEntity(
                            type=MessageEntityType.BOLD,
                            offset=open_tag_index,
                            length=close_tag_index - open_tag_index - len(open_tag)
                        )
                    )
                case "join":
                    entities.append(
                        MessageEntity(
                            type=MessageEntityType.TEXT_LINK,
                            offset=open_tag_index,
                            length=close_tag_index - open_tag_index - len(open_tag),
                            url=join_url
                        )
                    )
                case "player":
                    entities.append(
                        MessageEntity(
                            type=MessageEntityType.TEXT_MENTION,
                            offset=open_tag_index,
                            length=close_tag_index - open_tag_index - len(open_tag),
                            user=AiogramUser(
                                id=players[player_index].telegram_id,
                                first_name=players[player_index].first_name,
                                is_bot=False
                            )
                        )
                    )
                    entities.append(
                        MessageEntity(
                            type=MessageEntityType.ITALIC,
                            offset=open_tag_index,
                            length=close_tag_index - open_tag_index - len(open_tag)
                        )
                    )
                    player_index += 1

            text = (
                    text[:open_tag_index]
                    + text[open_tag_index + len(open_tag):close_tag_index]
                    + text[close_tag_index + len(close_tag):]
            )

        return text, entities
