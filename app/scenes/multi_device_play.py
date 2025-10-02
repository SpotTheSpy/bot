import asyncio
import logging
from asyncio import Task
from typing import Dict, List, Tuple
from uuid import UUID

from aiogram import Bot
from aiogram.enums import MessageEntityType
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message, MessageEntity, User as AiogramUser, BufferedInputFile
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.i18n import gettext as _
from aiohttp import ClientSession

from app.actions.back import BackAction
from app.actions.menu import MenuAction
from app.actions.multi_device_finish import MultiDeviceFinishAction
from app.actions.multi_device_leave import MultiDeviceLeaveAction
from app.actions.multi_device_play_again import MultiDevicePlayAgainAction
from app.actions.multi_device_start import MultiDeviceStartAction
from app.controllers.multi_device_games import MultiDeviceGamesController
from app.data.secret_words_controller import SecretWordsController
from app.enums.payload_type import PayloadType
from app.enums.player_role import PlayerRole
from app.exceptions.already_in_game import AlreadyInGameError
from app.exceptions.api import APIError
from app.exceptions.game_has_already_started import GameHasAlreadyStartedError
from app.exceptions.invalid_player_amount import InvalidPlayerAmountError
from app.exceptions.not_found import NotFoundError
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.models.multi_device_game import MultiDeviceGame, MultiDevicePlayer
from app.models.user import User
from app.parameters import Parameters
from app.scenes.base import BaseScene


def _get_entities(
        text: str,
        *,
        join_url: str | None = None,
        players: List[MultiDevicePlayer] | None = None
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
                        offset=open_tag_index + 1,
                        length=close_tag_index - open_tag_index - len(open_tag)
                    )
                )
            case "join":
                entities.append(
                    MessageEntity(
                        type=MessageEntityType.TEXT_LINK,
                        offset=open_tag_index + 1,
                        length=close_tag_index - open_tag_index - len(open_tag),
                        url=join_url
                    )
                )
            case "player":
                entities.append(
                    MessageEntity(
                        type=MessageEntityType.TEXT_MENTION,
                        offset=open_tag_index + 1,
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
                        offset=open_tag_index + 1,
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


async def _create_join_url(
        bot: Bot,
        game_id: UUID
) -> str:
    return await create_start_link(bot, f"{PayloadType.JOIN}:{game_id}", encode=True)


async def _get_qr_code(qr_code_url: str) -> BufferedInputFile | None:
    async with ClientSession() as session:
        async with session.get(qr_code_url) as response:
            if response.status == 200:
                return BufferedInputFile(
                    await response.read(),
                    "qr.jpg"
                )


class MultiDeviceGameMessages:
    def __init__(self) -> None:
        self._update_tasks: Dict[UUID, Task] = {}
        self._messages: Dict[UUID, Dict[UUID, Message]] = {}

    def add_message(
            self,
            game_id: UUID,
            user_id: UUID,
            message: Message
    ) -> None:
        if game_id not in self._messages:
            self._messages[game_id] = {}

        self._messages[game_id][user_id] = message

    def get_messages(
            self,
            game_id: UUID,
    ) -> Dict[UUID, Message]:
        return self._messages.get(game_id)

    def remove_message(
            self,
            game_id: UUID,
            user_id: UUID
    ) -> None:
        if game_id in self._messages:
            self._messages[game_id].pop(user_id)

        if not self._messages[game_id]:
            self._messages.pop(game_id)

    def clear_messages(
            self,
            game_id: UUID
    ) -> Dict[UUID, Message] | None:
        if game_id not in self._messages:
            return

        messages: Dict[UUID, Message] = self.get_messages(game_id).copy()

        self._messages.pop(game_id)
        return messages

    def start_update_recruitment(
            self,
            game_id: UUID,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        if game_id in self._update_tasks:
            self._update_tasks[game_id].cancel()

        task: Task = asyncio.create_task(
            self._update_recruitment_messages(
                game_id,
                self._messages.get(game_id),
                state,
                multi_device_games
            )
        )

        self._update_tasks[game_id] = task

    def stop_update_recruitment(
            self,
            game_id: UUID
    ) -> None:
        if game_id in self._update_tasks:
            self._update_tasks[game_id].cancel()
            self._update_tasks.pop(game_id)

    async def _update_recruitment_messages(
            self,
            game_id: UUID,
            messages: Dict[UUID, Message],
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        try:
            while True:
                if not messages:
                    return
                await asyncio.sleep(Parameters.API_POLLING_TIMEOUT)

                game: MultiDeviceGame | None = await multi_device_games.get_game(game_id)

                if game is None:
                    return

                await state.update_data(game=game.to_json())

                await asyncio.gather(
                    *[
                        self.update_recruitment_message(
                            game,
                            user_id,
                            message
                        )
                        for user_id, message in messages.copy().items()
                    ]
                )
        except Exception as e:
            logging.exception(e)

    async def new_recruitment_message(
            self,
            game: MultiDeviceGame,
            user_id: UUID,
            message: Message,
            qr_code: BufferedInputFile
    ) -> Message:
        text, entities = await self._create_recruitment_message(game, message.bot)

        return await message.answer_photo(
            qr_code,
            caption=text,
            entities=entities,
            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                is_host=user_id == game.host_id
            )
        )

    async def update_recruitment_message(
            self,
            game: MultiDeviceGame,
            user_id: UUID,
            message: Message,
            qr_code: BufferedInputFile | None = None
    ) -> Message:
        text, entities = await self._create_recruitment_message(game, message.bot)

        return await MultiDevicePlayScene.edit_message(
            message,
            text,
            qr_code,
            entities=entities,
            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                is_host=user_id == game.host_id
            ),
            only_edit_caption=qr_code is None
        )

    @staticmethod
    async def _create_recruitment_message(
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

        return _get_entities(
            _("message.multi_device.play.recruit").format(
                players="\n".join(players),
                player_amount=len(game.players),
                max_player_amount=game.player_amount
            ),
            join_url=await _create_join_url(bot, game.game_id),
            players=game.players
        )


class MultiDevicePlayScene(BaseScene, state="multi_device_play"):
    messages = MultiDeviceGameMessages()

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            player_amount: int,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game: MultiDeviceGame = await multi_device_games.create_game(
            user.id,
            player_amount
        )
        game = await multi_device_games.set_game_url(
            game.game_id,
            await _create_join_url(callback_query.bot, game.game_id)
        )

        await state.update_data(game=game.to_json())

        new_message: Message = await self.messages.update_recruitment_message(
            game,
            user.id,
            callback_query.message,
            await _get_qr_code(game.qr_code_url)
        )

        self.messages.add_message(
            game.game_id,
            user.id,
            new_message
        )

        self.messages.start_update_recruitment(
            game.game_id,
            state,
            multi_device_games
        )

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            command: CommandObject,
            user: User,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
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

        new_message: Message = await self.messages.new_recruitment_message(
            game,
            user.id,
            message,
            await _get_qr_code(game.qr_code_url)
        )
        self.messages.add_message(
            game.game_id,
            user.id,
            new_message
        )

        await message.delete()

    @on.callback_query(MultiDeviceStartAction.filter())
    async def on_start(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game: MultiDeviceGame = await MultiDeviceGame.from_context(
            user.id,
            state,
            multi_device_games
        )

        try:
            game = await multi_device_games.start_game(game.game_id)
        except InvalidPlayerAmountError:
            await callback_query.answer(_("answer.multi_device.play.too_few_players"))
            return
        except NotFoundError:
            return

        await state.update_data(game=game.to_json())

        self.messages.stop_update_recruitment(game.game_id)

        players: Dict[UUID, MultiDevicePlayer] = {player.user_id: player for player in game.players}

        for user_id, message in self.messages.get_messages(game.game_id).copy().items():
            role: PlayerRole = players[user_id].role

            if role is None:
                return

            message_text: str = {
                PlayerRole.CITIZEN: _("message.multi_device.play.view_role.citizen"),
                PlayerRole.SPY: _("message.multi_device.play.view_role.spy")
            }.get(role)

            new_message: Message | None = await MultiDevicePlayScene.edit_message(
                message,
                message_text.format(
                    secret_word=SecretWordsController.get_secret_word(game.secret_word)
                ),
                reply_markup=InlineKeyboardFactory.multi_device_view_role_keyboard(
                    is_host=user_id == game.host_id
                )
            )

            if new_message is not None:
                self.messages.get_messages(game.game_id)[user_id] = new_message

    @on.callback_query(MultiDeviceFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game: MultiDeviceGame | None = await MultiDeviceGame.from_context(
            user.id,
            state,
            multi_device_games
        )

        try:
            spy: MultiDevicePlayer = [player for player in game.players if player.role == PlayerRole.SPY][0]
        except IndexError:
            return

        message_text, entities = _get_entities(
            _("message.multi_device.play.finish").format(
                secret_word=SecretWordsController.get_secret_word(game.secret_word),
                first_name=spy.first_name
            ),
            players=[spy]
        )

        for user_id, message in self.messages.get_messages(game.game_id).copy().items():
            new_message: Message | None = await MultiDevicePlayScene.edit_message(
                message,
                message_text,
                entities=entities,
                reply_markup=InlineKeyboardFactory.multi_device_play_again_keyboard(
                    is_host=user_id == game.host_id
                )
            )

            if new_message is not None:
                self.messages.get_messages(game.game_id)[user_id] = new_message

    @on.callback_query(MultiDevicePlayAgainAction.filter())
    async def on_play_again(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game: MultiDeviceGame | None = await MultiDeviceGame.from_context(
            user.id,
            state,
            multi_device_games
        )

        messages: Dict[UUID, Message] = self.messages.clear_messages(game.game_id)
        players: List[MultiDevicePlayer] = game.players

        await multi_device_games.remove_game(game.game_id)

        game: MultiDeviceGame = await multi_device_games.create_game(
            user.id,
            game.player_amount
        )
        game = await multi_device_games.set_game_url(
            game.game_id,
            await _create_join_url(callback_query.bot, game.game_id)
        )

        for player in players:
            if player.user_id == user.id:
                continue

            try:
                game = await multi_device_games.join_game(
                    game.game_id,
                    player.user_id
                )
            except APIError:
                continue

        await state.update_data(game=game.to_json())

        qr_code: BufferedInputFile = await _get_qr_code(game.qr_code_url)

        new_messages: Tuple[Message | None] = await asyncio.gather(
            *[
                self.messages.update_recruitment_message(
                    game,
                    user_id,
                    message,
                    qr_code
                )
                for user_id, message in messages.items()
            ]
        )

        for user_id, message in zip(messages.keys(), new_messages):
            if message is not None:
                self.messages.add_message(
                    game.game_id,
                    user_id,
                    message
                )

        self.messages.start_update_recruitment(
            game.game_id,
            state,
            multi_device_games
        )

    @on.callback_query(MultiDeviceLeaveAction.filter())
    async def on_leave(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.leave()

    @on.callback_query.leave()
    async def on_scene_leave(
            self,
            callback_query: CallbackQuery,
            user: User,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)

        if game is None:
            return

        if user.id == game.host_id:
            await multi_device_games.remove_game(game.game_id)

            for user_id, message in self.messages.get_messages(game.game_id).items():
                if user_id == game.host_id:
                    continue

                await MultiDevicePlayScene.edit_message(
                    message,
                    _("message.multi_device.play.stop")
                )

            self.messages.stop_update_recruitment(game.game_id)
            self.messages.clear_messages(game.game_id)
        else:
            await multi_device_games.leave_game(
                game.game_id,
                user.id
            )

            await self.edit_message(
                callback_query.message,
                _("message.multi_device.play.leave")
            )

            self.messages.remove_message(game.game_id, user.id)

    @on.callback_query(MenuAction.filter())
    async def on_menu(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.goto("start")

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery,
            user: User,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)

        if game is not None:
            player_amount: int | None = game.player_amount
        else:
            player_amount = None

        await self.wizard.back(player_amount=player_amount)

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
