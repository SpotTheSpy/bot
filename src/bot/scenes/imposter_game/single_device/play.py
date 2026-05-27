from uuid import UUID

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext

from src.bot.actions.imposter_game.single_device.view_question import SingleDeviceImposterGameViewQuestionAction
from src.bot.exceptions.game import GameError
from src.bot.keyboards.imposter_game.single_device.proceed import single_device_impostor_game_proceed_keyboard
from src.bot.keyboards.imposter_game.single_device.view_role import single_device_imposter_game_view_question_keyboard
from src.bot.logger import logger
from src.bot.scenes.base import BaseScene
from src.core.controllers.redis import RedisController
from src.core.enums.imposter_count import ImposterCount
from src.core.enums.imposter_player_role import ImposterPlayerRole
from src.core.enums.time_stamp import TimeStamp
from src.core.models.redis.imposter_game.imposter_question_queue import ImposterQuestionQueue
from src.core.models.redis.imposter_game.single_device import SingleDeviceImposterGame
from src.core.models.redis.user import User


class SingleDeviceImposterGamePlayScene(BaseScene, state="single_device_imposter_game_play"):
    """
    Scene for playing a single-device imposter game.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            player_count: int,
            imposter_count: ImposterCount,
            user_controller: RedisController[User],
            single_device_imposter_game_controller: RedisController[SingleDeviceImposterGame],
            imposter_question_controller: RedisController[ImposterQuestionQueue],
    ) -> None:
        if user.active_games.active_single_device_imposter_game is not None:
            await single_device_imposter_game_controller.remove(user.active_games.active_single_device_imposter_game)

        imposter_question_queue: ImposterQuestionQueue | None = await imposter_question_controller.get(user.id)

        if imposter_question_queue is None:
            imposter_question_queue: ImposterQuestionQueue = ImposterQuestionQueue.new(
                user.id,
            )

        real_question, imposter_question = imposter_question_queue.get_unique_question_pair()

        game: SingleDeviceImposterGame = SingleDeviceImposterGame.new(
            user.id,
            player_count,
            real_question,
            imposter_question,
            imposter_count,
        )
        user.active_games.active_single_device_imposter_game = game.id

        await single_device_imposter_game_controller.set(game)
        await imposter_question_controller.set(imposter_question_queue, expire=TimeStamp.DAY)
        await user_controller.set(user, expire=TimeStamp.DAY)

        await state.update_data(
            player_index=0,
            anticipate_input=False,
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-imposter-game-prepare",
                player_index=1,
                player_count=game.player_count,
            ),
            reply_markup=single_device_imposter_game_view_question_keyboard(),
        )

        await callback_query.answer()

        logger.info(
            f"{user.telegram_id} ({user.first_name}) started a single-device imposter game."
        )

    @on.callback_query(SingleDeviceImposterGameViewQuestionAction.filter())
    async def on_view_question(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            single_device_imposter_game_controller: RedisController[SingleDeviceImposterGame],
    ) -> None:
        game_id: UUID | None = user.active_games.active_single_device_imposter_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceImposterGame | None = await single_device_imposter_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")
        player_index: int | None = await state.get_value("player_index")
        if player_index is None:
            raise GameError("Player index was not found.")

        role: ImposterPlayerRole = (
            ImposterPlayerRole.IMPOSTER
            if player_index in game.imposter_indices
            else ImposterPlayerRole.CITIZEN
        )

        question: str = (
            game.real_question
            if role == ImposterPlayerRole.CITIZEN
            else game.imposter_question
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-impostor-game-view-question",
                question=i18n.get(f"imposter-question-{question}"),
            ),
            reply_markup=single_device_impostor_game_proceed_keyboard(),
        )

        await callback_query.answer()
