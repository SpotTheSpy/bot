import asyncio
from asyncio import Task, create_task
from typing import List, Tuple
from uuid import UUID

from aiogram import Bot
from aiogram.enums import MessageEntityType
from aiogram.filters import CommandObject
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message, MessageEntity, User as AiogramUser, BufferedInputFile
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.i18n import gettext as _
from aiohttp import ClientSession
from babel.support import LazyProxy

from app.actions.multi_device_finish import MultiDeviceFinishAction
from app.actions.multi_device_leave import MultiDeviceLeaveAction
from app.actions.multi_device_play_again import MultiDevicePlayAgainAction
from app.actions.multi_device_start import MultiDeviceStartAction
from app.controllers.api.multi_device_games import MultiDeviceGamesController
from app.controllers.redis.bot_users import BotUsersController
from app.data.secret_words_controller import SecretWordsController
from app.enums.payload_type import PayloadType
from app.enums.player_role import PlayerRole
from app.exceptions.already_in_game import AlreadyInGameError
from app.exceptions.api import APIError
from app.exceptions.game_has_already_started import GameHasAlreadyStartedError
from app.exceptions.invalid_player_amount import InvalidPlayerAmountError
from app.exceptions.not_found import NotFoundError
from app.models.multi_device_game import MultiDeviceGame, MultiDevicePlayer
from app.models.user import User, BotUser
from app.scenes.base import BaseScene
from app.utils.dict_factory import DictFactory
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.utils.logging import logger


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


async def _create_recruitment_message(
        game: MultiDeviceGame,
        bot: Bot,
        *,
        locale: str | None = None
) -> Tuple[str, List[MessageEntity]]:
    players: List[str] = []

    for index, player in enumerate(game.players):
        if player.user_id == game.host_id:
            players.append(
                _("message.multi_device.play.recruit.player.host", locale=locale).format(
                    index=index + 1,
                    first_name=player.first_name
                )
            )
        else:
            players.append(
                _("message.multi_device.play.recruit.player", locale=locale).format(
                    index=index + 1,
                    first_name=player.first_name
                )
            )

    return _get_entities(
        _("message.multi_device.play.recruit", locale=locale).format(
            players="\n".join(players),
            player_amount=len(game.players),
            max_player_amount=game.player_amount
        ),
        join_url=await _create_join_url(bot, game.game_id),
        players=game.players
    )


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


class MultiDevicePlayScene(BaseScene, state="multi_device_play"):
    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            player_amount: int,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        try:
            game: MultiDeviceGame = await multi_device_games.create_game(
                user.id,
                player_amount
            )
        except AlreadyInGameError:
            game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)
            await multi_device_games.remove_game(game.game_id)

            try:
                game: MultiDeviceGame | None = await multi_device_games.create_game(
                    user.id,
                    player_amount
                )
            except Exception as e:
                await callback_query.answer()
                logger.error(
                    f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                    f"Failed to create multi-device game. Exception: {e}"
                )
                return

        if game is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to create multi-device game"
            )
            return

        game: MultiDeviceGame = await multi_device_games.set_game_url(
            game.game_id,
            await _create_join_url(callback_query.bot, game.game_id)
        )

        text, entities = await _create_recruitment_message(game, user.bot)
        qr_code: BufferedInputFile = await _get_qr_code(game.qr_code_url)

        await user.edit_message(
            text=text,
            photo=qr_code,
            entities=entities,
            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(is_host=True)
        )

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"started recruitment for a multi-device game (game_id={game.game_id})"
        )

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            command: CommandObject,
            user: BotUser,
            multi_device_games: MultiDeviceGamesController,
            bot_users: BotUsersController
    ) -> None:
        payload: str = command.args

        if not payload.startswith(PayloadType.JOIN):
            await message.delete()
            return

        try:
            game_id = UUID(payload.split(":")[1])
        except (ValueError, IndexError):
            await message.delete()
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

        text, entities = await _create_recruitment_message(game, message.bot)
        qr_code: BufferedInputFile = await _get_qr_code(game.qr_code_url)

        await user.new_message(
            chat_id=message.chat.id,
            text=text,
            photo=qr_code,
            entities=entities,
            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard()
        )

        await message.delete()

        tasks: List[Task] = []

        for player in game.players:
            if user.id == player.user_id:
                continue

            player_bot_user: BotUser = await bot_users.get_bot_user(player.user_id, user.bot)

            if player_bot_user is None:
                continue

            text, entities = await _create_recruitment_message(game, message.bot, locale=player_bot_user.locale)

            tasks.append(
                create_task(
                    player_bot_user.edit_message(
                        text=text,
                        entities=entities,
                        reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                            is_host=player.user_id == game.host_id,
                            locale=player_bot_user.locale
                        ),
                        only_edit_caption=True
                    )
                )
            )

        await asyncio.gather(*tasks)

        logger.info(
            f"{message.from_user.first_name} (id={message.from_user.id}) "
            f"joined a multi-device game (game_id={game.game_id})"
        )

    @on.callback_query(MultiDeviceStartAction.filter())
    async def on_start(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            multi_device_games: MultiDeviceGamesController,
            bot_users: BotUsersController
    ) -> None:
        game: MultiDeviceGame = await multi_device_games.get_game_by_user_id(user.id)

        if game is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to start in a multi-device game because the game was not found"
            )
            return

        try:
            game = await multi_device_games.start_game(game.game_id)
        except InvalidPlayerAmountError:
            await callback_query.answer(_("answer.multi_device.play.too_few_players"))
            return

        tasks: List[Task] = []

        for player in game.players:
            player_bot_user: BotUser = await bot_users.get_bot_user(player.user_id, user.bot)

            if player_bot_user is None:
                continue

            message_text: LazyProxy = DictFactory.multi_device_role_message(
                locale=player_bot_user.locale
            ).get(player.role)

            tasks.append(
                create_task(
                    player_bot_user.edit_message(
                        text=message_text.format(
                            secret_word=SecretWordsController.get_secret_word(
                                game.secret_word,
                                locale=player_bot_user.locale
                            )
                        ),
                        reply_markup=InlineKeyboardFactory.multi_device_view_role_keyboard(
                            is_host=player.user_id == game.host_id,
                            locale=player_bot_user.locale
                        )
                    )
                )
            )

        await asyncio.gather(*tasks)

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"started a multi-device game (game_id={game.game_id})"
        )

    @on.callback_query(MultiDeviceFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            multi_device_games: MultiDeviceGamesController,
            bot_users: BotUsersController
    ) -> None:
        game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)

        if game is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to finish a multi-device game because the game was not found"
            )
            return

        try:
            spy: MultiDevicePlayer = [player for player in game.players if player.role == PlayerRole.SPY][0]
        except IndexError:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to finish a multi-device game because the game has no spy"
            )
            return

        tasks: List[Task] = []

        for player in game.players:
            player_bot_user: BotUser = await bot_users.get_bot_user(player.user_id, user.bot)

            if player_bot_user is None:
                continue

            message_text, entities = _get_entities(
                _("message.multi_device.play.finish", locale=player_bot_user.locale).format(
                    secret_word=SecretWordsController.get_secret_word(
                        game.secret_word,
                        locale=player_bot_user.locale
                    ),
                    first_name=spy.first_name
                ),
                players=[spy]
            )

            tasks.append(
                create_task(
                    player_bot_user.edit_message(
                        text=message_text,
                        entities=entities,
                        reply_markup=InlineKeyboardFactory.multi_device_play_again_keyboard(
                            is_host=player.user_id == game.host_id,
                            locale=player_bot_user.locale
                        )
                    )
                )
            )

        await asyncio.gather(*tasks)

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"finished a multi-device game (game_id={game.game_id})"
        )

    @on.callback_query(MultiDevicePlayAgainAction.filter())
    async def on_play_again(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            multi_device_games: MultiDeviceGamesController,
            bot_users: BotUsersController
    ) -> None:
        game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)
        players: List[MultiDevicePlayer] = game.players

        if game is not None:
            await multi_device_games.remove_game(game.game_id)

        try:
            game: MultiDeviceGame | None = await multi_device_games.create_game(
                user.id,
                game.player_amount
            )
        except Exception as e:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"Failed to create multi-device game. Exception: {e}"
            )
            return

        game: MultiDeviceGame = await multi_device_games.set_game_url(
            game.game_id,
            await _create_join_url(callback_query.bot, game.game_id)
        )

        for player in players:
            if player.user_id == user.id:
                continue

            try:
                game: MultiDeviceGame = await multi_device_games.join_game(
                    game.game_id,
                    player.user_id
                )
            except APIError:
                continue

        qr_code: BufferedInputFile = await _get_qr_code(game.qr_code_url)
        tasks: List[Task] = []

        for player in game.players:
            player_bot_user: BotUser = await bot_users.get_bot_user(player.user_id, user.bot)

            if player_bot_user is None:
                continue

            text, entities = await _create_recruitment_message(game, user.bot, locale=player_bot_user.locale)

            tasks.append(
                create_task(
                    player_bot_user.edit_message(
                        text=text,
                        photo=qr_code,
                        entities=entities,
                        reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                            is_host=player.user_id == game.host_id,
                            locale=player_bot_user.locale
                        )
                    )
                )
            )

        await asyncio.gather(*tasks)

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"started recruitment for a multi-device game (game_id={game.game_id})"
        )

    @on.callback_query(MultiDeviceLeaveAction.filter())
    async def on_leave(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.leave()

    async def on_scene_leave(
            self,
            user: BotUser,
            multi_device_games: MultiDeviceGamesController,
            bot_users: BotUsersController
    ) -> None:
        game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)

        if game is None:
            return

        if user.id == game.host_id:
            await multi_device_games.remove_game(game.game_id)

            tasks: List[Task] = []

            for player in game.players:
                if player.user_id == user.id:
                    continue

                player_bot_user: BotUser = await bot_users.get_bot_user(player.user_id, user.bot)

                if player_bot_user is None:
                    continue

                tasks.append(
                    create_task(
                        player_bot_user.edit_message(
                            text=_("message.multi_device.play.stop", locale=player_bot_user.locale)
                        )
                    )
                )

            await asyncio.gather(*tasks)

            logger.info(
                f"{user.first_name} (id={user.telegram_id}) "
                f"finished a multi-device game (game_id={game.game_id})"
            )
        else:
            try:
                game: MultiDeviceGame | None = await multi_device_games.leave_game(
                    game.game_id,
                    user.id
                )
            except APIError:
                return

            await user.edit_message(
                text=_("message.multi_device.play.leave")
            )

            if game.has_started:
                return

            tasks: List[Task] = []

            for player in game.players:
                if player.user_id == user.id:
                    continue

                player_bot_user: BotUser = await bot_users.get_bot_user(player.user_id, user.bot)

                if player_bot_user is None:
                    continue

                text, entities = await _create_recruitment_message(game, user.bot, locale=player_bot_user.locale)

                tasks.append(
                    create_task(
                        player_bot_user.edit_message(
                            text=text,
                            entities=entities,
                            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                                is_host=player.user_id == game.host_id,
                                locale=player_bot_user.locale
                            ),
                            only_edit_caption=True
                        )
                    )
                )

            await asyncio.gather(*tasks)

            logger.info(
                f"{user.first_name} (id={user.telegram_id}) "
                f"left a multi-device game (game_id={game.game_id})"
            )

    async def on_back(
            self,
            user: User,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)

        if game is not None:
            player_amount: int | None = game.player_amount
        else:
            player_amount = None

        await self.wizard.back(
            user=user,
            player_amount=player_amount
        )

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
