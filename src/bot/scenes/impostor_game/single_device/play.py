from uuid import UUID

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext

from src.bot.actions.impostor_game.single_device.view_question import SingleDeviceImpostorGameViewQuestionAction
from src.bot.exceptions.game import GameError
from src.bot.keyboards.impostor_game.single_device.proceed import single_device_impostor_game_proceed_keyboard
from src.bot.keyboards.impostor_game.single_device.view_role import single_device_impostor_game_view_question_keyboard
from src.bot.logger import logger
from src.bot.scenes.base import BaseScene
from src.core.controllers.redis import RedisController
from src.core.enums.impostor_count import ImpostorCount
from src.core.enums.impostor_player_role import ImpostorPlayerRole
from src.core.enums.time_stamp import TimeStamp
from src.core.models.redis.impostor_game.impostor_question_queue import ImpostorQuestionQueue
from src.core.models.redis.impostor_game.single_device import SingleDeviceImpostorGame
from src.core.models.redis.user import User


class SingleDeviceImpostorGamePlayScene(BaseScene, state="single_device_impostor_game_play"):
    """
    Scene for playing a single-device impostor game.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            player_count: int,
            impostor_count: ImpostorCount,
            user_controller: RedisController[User],
            single_device_impostor_game_controller: RedisController[SingleDeviceImpostorGame],
            impostor_question_controller: RedisController[ImpostorQuestionQueue],
    ) -> None:
        if user.active_games.active_single_device_impostor_game is not None:
            await single_device_impostor_game_controller.remove(user.active_games.active_single_device_impostor_game)

        impostor_question_queue: ImpostorQuestionQueue | None = await impostor_question_controller.get(user.id)

        if impostor_question_queue is None:
            impostor_question_queue: ImpostorQuestionQueue = ImpostorQuestionQueue.new(
                user.id,
            )

        real_question, impostor_question = impostor_question_queue.get_unique_question_pair()

        game: SingleDeviceImpostorGame = SingleDeviceImpostorGame.new(
            user.id,
            player_count,
            real_question,
            impostor_question,
            impostor_count,
        )
        user.active_games.active_single_device_impostor_game = game.id

        await single_device_impostor_game_controller.set(game)
        await impostor_question_controller.set(impostor_question_queue, expire=TimeStamp.DAY)
        await user_controller.set(user, expire=TimeStamp.DAY)

        await state.update_data(
            player_index=0,
            anticipate_input=False,
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-impostor-game-prepare",
                player_index=1,
                player_count=game.player_count,
            ),
            reply_markup=single_device_impostor_game_view_question_keyboard(),
        )

        await callback_query.answer()

        logger.info(
            f"{user.telegram_id} ({user.first_name}) started a single-device impostor game."
        )

    @on.callback_query(SingleDeviceImpostorGameViewQuestionAction.filter())
    async def on_view_question(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            single_device_impostor_game_controller: RedisController[SingleDeviceImpostorGame],
    ) -> None:
        game_id: UUID | None = user.active_games.active_single_device_impostor_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceImpostorGame | None = await single_device_impostor_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")
        player_index: int | None = await state.get_value("player_index")
        if player_index is None:
            raise GameError("Player index was not found.")

        role: ImpostorPlayerRole = (
            ImpostorPlayerRole.IMPOSTOR
            if player_index in game.impostor_indices
            else ImpostorPlayerRole.CITIZEN
        )

        question: str = (
            game.real_question
            if role == ImpostorPlayerRole.CITIZEN
            else game.impostor_question
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-impostor-game-view-question",
                question=i18n.get(f"impostor-question-{question}"),
            ),
            reply_markup=single_device_impostor_game_proceed_keyboard(),
        )

        await callback_query.answer()
