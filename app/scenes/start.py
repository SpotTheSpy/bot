import asyncio
from asyncio import Task, create_task
from typing import List

from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.controllers.multi_device_games import MultiDeviceGamesController
from app.controllers.redis import RedisController
from app.controllers.single_device_games import SingleDeviceGamesController
from app.exceptions.api import APIError
from app.models.bot_user import BotUser
from app.models.multi_device_game import MultiDeviceGame
from app.models.single_device_game import SingleDeviceGame
from app.scenes.base import BaseScene
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.utils.logging import logger


class StartScene(BaseScene, state="start", reset_history_on_enter=True):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user: BotUser,
            locale: str | None = None
    ) -> None:
        await user.new_start_message(locale=locale)

        logger.info(
            f"{message.from_user.first_name} (id={message.from_user.id}) "
            f"opened the start page"
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            locale: str | None = None
    ) -> None:
        await user.start_message(locale=locale)
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()

    @classmethod
    async def _reset_game_data(
            cls,
            user: BotUser,
            single_device_games: SingleDeviceGamesController,
            multi_device_games: MultiDeviceGamesController,
            bot_users: RedisController[BotUser]
    ) -> None:
        await asyncio.gather(
            cls._reset_single_device_game_data(user, single_device_games),
            cls._reset_multi_device_game_data(user, multi_device_games, bot_users)
        )

    @staticmethod
    async def _reset_single_device_game_data(
            user: BotUser,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame = await single_device_games.get_game_by_user_id(user.id)

        if game is None:
            return

        await single_device_games.remove_game(game.game_id)

    @staticmethod
    async def _reset_multi_device_game_data(
            user: BotUser,
            multi_device_games: MultiDeviceGamesController,
            bot_users: RedisController[BotUser]
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

                player_bot_user: BotUser = await bot_users.get(
                    player.user_id,
                    bot=user.bot,
                    i18n=user.i18n,
                    from_json_method=BotUser.from_data
                )

                if player_bot_user is None:
                    continue

                with player_bot_user.i18n.use_locale(player_bot_user.locale):
                    tasks.append(
                        create_task(
                            player_bot_user.edit_message(
                                text=_("message.multi_device.play.stop")
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

                player_bot_user: BotUser = await bot_users.get(
                    player.user_id,
                    bot=user.bot,
                    i18n=user.i18n,
                    from_json_method=BotUser.from_data
                )

                if player_bot_user is None:
                    continue

                with player_bot_user.i18n.use_locale(player_bot_user.locale):
                    text, entities = self._create_recruitment_message(game)

                    tasks.append(
                        create_task(
                            player_bot_user.edit_message(
                                text=text,
                                entities=entities,
                                reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                                    is_host=player.user_id == game.host_id
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
