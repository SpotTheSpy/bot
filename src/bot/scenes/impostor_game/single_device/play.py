from uuid import UUID

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from src.bot.actions.impostor_game.single_device.finish import SingleDeviceImpostorGameFinishAction
from src.bot.actions.impostor_game.single_device.next_answer import SingleDeviceImpostorGameNextAnswerAction
from src.bot.actions.impostor_game.single_device.play_again import SingleDeviceImpostorGamePlayAgainAction
from src.bot.actions.impostor_game.single_device.proceed import SingleDeviceImpostorGameProceedAction
from src.bot.actions.impostor_game.single_device.view_question import SingleDeviceImpostorGameViewQuestionAction
from src.bot.exceptions.game import GameError
from src.bot.keyboards.impostor_game.single_device.next_answer import single_device_impostor_game_next_answer_keyboard
from src.bot.keyboards.impostor_game.single_device.proceed import single_device_impostor_game_proceed_keyboard
from src.bot.keyboards.impostor_game.single_device.results import single_device_impostor_game_results_keyboard
from src.bot.keyboards.impostor_game.single_device.view_role import single_device_impostor_game_view_question_keyboard
from src.bot.logger import logger
from src.bot.scenes.base import BaseScene
from src.core.controllers.postgres import PostgresController
from src.core.controllers.redis import RedisController
from src.core.enums.impostor_count import ImpostorCount
from src.core.enums.impostor_player_role import ImpostorPlayerRole
from src.core.enums.time_stamp import TimeStamp
from src.core.models.redis.impostor_game.impostor_question_queue import ImpostorQuestionQueue
from src.core.models.redis.impostor_game.single_device import SingleDeviceImpostorGame
from src.core.models.redis.user import User
from aiogram import html
from src.core.models.postgres.single_device_impostor_game import (
    SingleDeviceImpostorGame as PostgresSingleDeviceImpostorGame
)


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
            answer=None,
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

        await state.update_data(
            anticipate_input=True,
        )

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
                answer=i18n.get("play-single-device-impostor-game-view-question.empty-answer"),
            ),
        )

        await callback_query.answer()

    @on.callback_query(SingleDeviceImpostorGameProceedAction.filter())
    async def on_proceed(
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

        game.answers[player_index] = await state.get_value("answer")
        await single_device_impostor_game_controller.set(game)

        player_index += 1

        if player_index >= game.player_count:
            await state.update_data(
                player_index=-1,
                anticipate_input=False,
                answer=None,
            )

            await user.message.edit(
                i18n.get(
                    "play-single-device-impostor-game-discuss",
                    question=i18n.get(f"impostor-question-{game.real_question}"),
                    answers=game.get_answers_as_string(i18n),
                ),
                reply_markup=single_device_impostor_game_next_answer_keyboard(),
            )

            await callback_query.answer()
            return

        await state.update_data(
            player_index=player_index,
            anticipate_input=False,
            answer=None,
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-impostor-game-prepare",
                player_index=player_index + 1,
                player_count=game.player_count,
            ),
            reply_markup=single_device_impostor_game_view_question_keyboard(),
        )

        await callback_query.answer()

    @on.callback_query(SingleDeviceImpostorGameNextAnswerAction.filter())
    async def on_next_answer(
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

        player_index += 1

        await state.update_data(
            player_index=player_index,
        )

        await user.message.edit(
            i18n.get(
                "play-single-device-impostor-game-discuss",
                question=i18n.get(f"impostor-question-{game.real_question}"),
                answers=game.get_answers_as_string(i18n, player_index),
            ),
            reply_markup=single_device_impostor_game_next_answer_keyboard(
                is_last_answer=player_index + 1 >= game.player_count
            ),
        )

        await callback_query.answer()

    @on.callback_query(SingleDeviceImpostorGameFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            user: User,
            i18n: I18nContext,
            postgres: PostgresController,
            single_device_impostor_game_controller: RedisController[SingleDeviceImpostorGame],
    ) -> None:
        game_id: UUID | None = user.active_games.active_single_device_impostor_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceImpostorGame | None = await single_device_impostor_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")

        impostors: str = ", ".join([str(spy + 1) for spy in game.impostor_indices])

        await user.message.edit(
            i18n.get(
                "play-single-device-impostor-game-results",
                count=len(game.impostor_indices),
                impostors=impostors,
                real_question=i18n.get(f"impostor-question-{game.real_question}"),
                impostor_question=i18n.get(f"impostor-question-{game.impostor_question}"),
            ),
            reply_markup=single_device_impostor_game_results_keyboard()
        )

        await callback_query.answer()

        async with postgres.session() as session:
            new_game: PostgresSingleDeviceImpostorGame = PostgresSingleDeviceImpostorGame(
                id=game.id,
                host_id=game.host_id,
                host_telegram_id=user.telegram_id,
                player_count=game.player_count,
                real_question=game.real_question,
                impostor_question=game.impostor_question,
                impostor_count=game.impostor_count,
                impostor_indices=game.impostor_indices,
                answers=game.answers,
            )

            session.add(new_game)
            await session.commit()

        logger.info(
            f"{user.telegram_id} ({user.first_name}) finished the single-device impostor game."
        )

    @on.callback_query(SingleDeviceImpostorGamePlayAgainAction.filter())
    async def on_play_again(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            user_controller: RedisController[User],
            single_device_impostor_game_controller: RedisController[SingleDeviceImpostorGame],
            impostor_question_controller: RedisController[ImpostorQuestionQueue],
    ) -> None:
        game_id: UUID | None = user.active_games.active_single_device_impostor_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceImpostorGame | None = await single_device_impostor_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")

        impostor_question_queue: ImpostorQuestionQueue | None = await impostor_question_controller.get(user.id)

        if impostor_question_queue is None:
            impostor_question_queue: ImpostorQuestionQueue = ImpostorQuestionQueue.new(
                user.id,
            )

        real_question, impostor_question = impostor_question_queue.get_unique_question_pair()

        await single_device_impostor_game_controller.remove(game)

        game: SingleDeviceImpostorGame = SingleDeviceImpostorGame.new(
            user.id,
            game.player_count,
            real_question,
            impostor_question,
            game.impostor_count,
        )
        user.active_games.active_single_device_impostor_game = game.id

        await single_device_impostor_game_controller.set(game)
        await impostor_question_controller.set(impostor_question_queue, expire=TimeStamp.DAY)
        await user_controller.set(user, expire=TimeStamp.DAY)

        await state.update_data(
            player_index=0,
            anticipate_input=False,
            answer=None,
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

    @on.callback_query.leave()
    async def on_leave(
            self,
            callback_query: CallbackQuery,
            user: User,
            user_controller: RedisController[User],
            impostor_question_controller: RedisController[ImpostorQuestionQueue],
    ) -> None:
        await impostor_question_controller.remove(user.active_games.active_single_device_impostor_game)
        user.active_games.active_single_device_impostor_game = None
        await user_controller.set(user, expire=TimeStamp.DAY)

        await callback_query.answer()

        logger.info(
            f"{user.telegram_id} ({user.first_name}) left the single-device impostor game."
        )

    @on.message()
    async def on_message(
            self,
            message: Message,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
            single_device_impostor_game_controller: RedisController[SingleDeviceImpostorGame],
    ) -> None:
        if not await state.get_value("anticipate_input"):
            await message.delete()
            return

        user_input: str = message.text.strip()

        if len(user_input) > 128:
            user_input = user_input[:128] + "..."

        if not user_input:
            await message.delete()
            return

        game_id: UUID | None = user.active_games.active_single_device_impostor_game
        if game_id is None:
            raise GameError("Game ID was not found.")
        game: SingleDeviceImpostorGame | None = await single_device_impostor_game_controller.get(game_id)
        if game is None:
            raise GameError("Game was not found.")
        player_index: int | None = await state.get_value("player_index")
        if player_index is None:
            raise GameError("Player index was not found.")

        await state.update_data(
            answer=user_input,
        )

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
                answer=html.quote(user_input),
            ),
            reply_markup=single_device_impostor_game_proceed_keyboard(),
            message_to_delete=message.message_id,
        )
