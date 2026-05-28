from uuid import UUID

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from src.bot.actions.spy_game.single_device.finish import SingleDeviceSpyGameFinishAction
from src.bot.actions.spy_game.single_device.play_again import SingleDeviceSpyGamePlayAgainAction
from src.bot.actions.spy_game.single_device.proceed import SingleDeviceSpyGameProceedAction
from src.bot.actions.spy_game.single_device.view_role import SingleDeviceSpyGameViewRoleAction
from src.bot.exceptions.game import GameError
from src.bot.keyboards.spy_game.single_device.discuss import single_device_spy_game_discuss_keyboard
from src.bot.keyboards.spy_game.single_device.proceed import single_device_spy_game_proceed_keyboard
from src.bot.keyboards.spy_game.single_device.results import single_device_spy_game_results_keyboard
from src.bot.keyboards.spy_game.single_device.view_role import single_device_spy_game_view_role_keyboard
from src.bot.logger import logger
from src.bot.scenes.base import BaseScene
from src.core.controllers.postgres import PostgresController
from src.core.controllers.redis import RedisController
from src.core.enums.spy_category import SpyCategory
from src.core.enums.spy_count import SpyCount
from src.core.enums.spy_player_role import SpyPlayerRole
from src.core.enums.time_stamp import TimeStamp
from src.core.models.postgres.single_device_spy_game import SingleDeviceSpyGame as PostgresSingleDeviceSpyGame
from src.core.models.redis.spy_game.secret_word_queue import SecretWordQueue
from src.core.models.redis.spy_game.single_device import SingleDeviceSpyGame
from src.core.models.redis.user import User


class SingleDeviceSpyGamePlayScene(BaseScene, state="single_device_spy_game_play"):
    """
    Scene for playing a single-device spy game.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            player_count: int,
            category: SpyCategory,
            spy_count: SpyCount,
            user_controller: RedisController[User],
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
            secret_word_controller: RedisController[SecretWordQueue],
    ) -> None:
        if user.active_games.active_single_device_spy_game is not None:
            await single_device_spy_game_controller.remove(user.active_games.active_single_device_spy_game)

        secret_word_queue: SecretWordQueue | None = await secret_word_controller.get(user.id)

        if secret_word_queue is None:
            secret_word_queue: SecretWordQueue = SecretWordQueue.new(
                user.id,
            )

        game: SingleDeviceSpyGame = SingleDeviceSpyGame.new(
            user.id,
            player_count,
            secret_word_queue.get_unique_word(category),
            category,
            spy_count,
        )
        user.active_games.active_single_device_spy_game = game.id

        await single_device_spy_game_controller.set(game)
        await secret_word_controller.set(secret_word_queue, expire=TimeStamp.DAY)
        await user_controller.set(user, expire=TimeStamp.DAY)

        await state.update_data(
            player_index=0,
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-spy-game-prepare",
                player_index=1,
                player_count=game.player_count,
            ),
            reply_markup=single_device_spy_game_view_role_keyboard()
        )

        await callback_query.answer()

        logger.info(
            f"{user.telegram_id} ({user.first_name}) started a single-device spy game."
        )

    @on.callback_query(SingleDeviceSpyGameViewRoleAction.filter())
    async def on_view_role(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
    ) -> None:
        game_id: UUID | None = user.active_games.active_single_device_spy_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceSpyGame | None = await single_device_spy_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")
        player_index: int | None = await state.get_value("player_index")
        if player_index is None:
            raise GameError("Player index was not found.")

        role: SpyPlayerRole = SpyPlayerRole.SPY if player_index in game.spy_indices else SpyPlayerRole.CITIZEN

        await user.message.edit(
            i18n.get(
                "play-single-device-spy-game-view-role",
                role=role,
                secret_word=i18n.get(f"secret-word-{game.secret_word}"),
            ),
            reply_markup=single_device_spy_game_proceed_keyboard()
        )

        await callback_query.answer()

    @on.callback_query(SingleDeviceSpyGameProceedAction.filter())
    async def on_proceed(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
    ) -> None:
        game_id: UUID | None = user.active_games.active_single_device_spy_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceSpyGame | None = await single_device_spy_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")
        player_index: int | None = await state.get_value("player_index")
        if player_index is None:
            raise GameError("Player index was not found.")

        player_index += 1

        if player_index >= game.player_count:
            await user.message.edit(
                i18n.get("play-single-device-spy-game-discuss"),
                reply_markup=single_device_spy_game_discuss_keyboard()
            )

            await callback_query.answer()

            return

        await state.update_data(
            player_index=player_index,
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-spy-game-prepare",
                player_index=player_index + 1,
                player_count=game.player_count,
            ),
            reply_markup=single_device_spy_game_view_role_keyboard()
        )

        await callback_query.answer()

    @on.callback_query(SingleDeviceSpyGameFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            user: User,
            i18n: I18nContext,
            postgres: PostgresController,
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
    ) -> None:
        game_id: UUID | None = user.active_games.active_single_device_spy_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceSpyGame | None = await single_device_spy_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")

        spies: str = ", ".join([str(spy + 1) for spy in game.spy_indices])

        await user.message.edit(
            i18n.get(
                "play-single-device-spy-game-results",
                count=len(game.spy_indices),
                spies=spies,
                secret_word=i18n.get(f"secret-word-{game.secret_word}"),
            ),
            reply_markup=single_device_spy_game_results_keyboard()
        )

        await callback_query.answer()

        async with postgres.session() as session:
            new_game: PostgresSingleDeviceSpyGame = PostgresSingleDeviceSpyGame(
                id=game.id,
                host_id=game.host_id,
                host_telegram_id=user.telegram_id,
                player_count=game.player_count,
                secret_word=game.secret_word,
                category=game.category,
                spy_count=game.spy_count,
                spy_indices=game.spy_indices,
            )

            session.add(new_game)
            await session.commit()

        logger.info(
            f"{user.telegram_id} ({user.first_name}) finished the single-device spy game."
        )

    @on.callback_query(SingleDeviceSpyGamePlayAgainAction.filter())
    async def on_play_again(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            user_controller: RedisController[User],
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
            secret_word_controller: RedisController[SecretWordQueue],
    ) -> None:
        game_id: UUID | None = user.active_games.active_single_device_spy_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceSpyGame | None = await single_device_spy_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")

        secret_word_queue: SecretWordQueue | None = await secret_word_controller.get(user.id)

        if secret_word_queue is None:
            secret_word_queue: SecretWordQueue = SecretWordQueue.new(
                user.id,
            )

        await single_device_spy_game_controller.remove(game.id)

        game: SingleDeviceSpyGame = SingleDeviceSpyGame.new(
            user.id,
            game.player_count,
            secret_word_queue.get_unique_word(game.category),
            game.category,
            game.spy_count,
        )
        user.active_games.active_single_device_spy_game = game.id

        await single_device_spy_game_controller.set(game)
        await secret_word_controller.set(secret_word_queue, expire=TimeStamp.DAY)
        await user_controller.set(user, expire=TimeStamp.DAY)

        await state.update_data(
            player_index=0,
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-spy-game-prepare",
                player_index=1,
                player_count=game.player_count,
            ),
            reply_markup=single_device_spy_game_view_role_keyboard()
        )

        await callback_query.answer()

        logger.info(
            f"{user.telegram_id} ({user.first_name}) started a single-device spy game."
        )

    @on.callback_query.leave()
    async def on_leave(
            self,
            callback_query: CallbackQuery,
            user: User,
            user_controller: RedisController[User],
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
    ) -> None:
        await single_device_spy_game_controller.remove(user.active_games.active_single_device_spy_game)
        user.active_games.active_single_device_spy_game = None
        await user_controller.set(user, expire=TimeStamp.DAY)

        await callback_query.answer()

        logger.info(
            f"{user.telegram_id} ({user.first_name}) left the single-device spy game."
        )

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
