from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from babel.support import LazyProxy

from app.actions.single_device_finish import SingleDeviceFinishAction
from app.actions.single_device_play_again import SingleDevicePlayAgainAction
from app.actions.single_device_proceed import SingleDeviceProceedPlayerAction
from app.actions.single_device_view_role import SingleDeviceViewRoleAction
from app.controllers.api.single_device_games import SingleDeviceGamesController
from app.data.secret_words_controller import SecretWordsController
from app.enums.player_role import PlayerRole
from app.exceptions.already_in_game import AlreadyInGameError
from app.models.single_device_game import SingleDeviceGame
from app.models.user import User, BotUser
from app.scenes.base import BaseScene
from app.utils.dict_factory import DictFactory
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.utils.logging import logger


class SingleDevicePlayScene(BaseScene, state="single_device_play"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            player_amount: int,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        try:
            game: SingleDeviceGame | None = await single_device_games.create_game(
                user.id,
                callback_query.from_user.id,
                player_amount
            )
        except AlreadyInGameError:
            game: SingleDeviceGame | None = await single_device_games.get_game_by_user_id(user.id)
            await single_device_games.remove_game(game.game_id)

            try:
                game: SingleDeviceGame | None = await single_device_games.create_game(
                    user.id,
                    callback_query.from_user.id,
                    player_amount
                )
            except Exception as e:
                await callback_query.answer()
                logger.error(
                    f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                    f"Failed to create single-device game. Exception: {e}"
                )
                return

        if game is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to create single-device game"
            )
            return

        player_index: int = 0

        await state.update_data(
            game=game.to_json(),
            player_index=player_index
        )

        await callback_query.answer()
        await user.edit_message(
            text=_("message.single_device.play.prepare").format(
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"started a single-device game"
        )

    @on.callback_query(SingleDeviceViewRoleAction.filter())
    async def on_view_role(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = (
                SingleDeviceGame.from_json(await state.get_value("game"))
                or await single_device_games.get_game_by_user_id(user.id)
        )

        if game is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to view role in a single-device game because the game was not found"
            )
            return

        player_index: int = await state.get_value("player_index")
        role: PlayerRole = PlayerRole.SPY if player_index == game.spy_index else PlayerRole.CITIZEN
        message_text: LazyProxy = DictFactory.single_device_role_message().get(role)

        if player_index is None or message_text is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to view role in a single-device game because of an internal server error"
            )
            return

        await callback_query.answer()
        await user.edit_message(
            text=message_text.format(
                secret_word=SecretWordsController.get_secret_word(game.secret_word),
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_proceed_keyboard()
        )

    @on.callback_query(SingleDeviceProceedPlayerAction.filter())
    async def on_proceed(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = (
                SingleDeviceGame.from_json(await state.get_value("game"))
                or await single_device_games.get_game_by_user_id(user.id)
        )

        if game is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to proceed a single-device game because the game was not found"
            )
            return

        player_index: int | None = await state.get_value("player_index")

        if player_index is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to proceed a single-device game because of an internal server error"
            )
            return

        player_index += 1

        if player_index >= game.player_amount:
            await callback_query.answer()
            await user.edit_message(
                text=_("message.single_device.play.discuss"),
                reply_markup=InlineKeyboardFactory.single_device_finish_keyboard()
            )
            return

        await state.update_data(player_index=player_index)

        await callback_query.answer()
        await user.edit_message(
            text=_("message.single_device.play.prepare").format(
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )

    @on.callback_query(SingleDeviceFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = (
                SingleDeviceGame.from_json(await state.get_value("game"))
                or await single_device_games.get_game_by_user_id(user.id)
        )

        if game is None:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"failed to finish a single-device game because the game was not found"
            )
            return

        await callback_query.answer()
        await user.edit_message(
            text=_("message.single_device.play.finish").format(
                secret_word=SecretWordsController.get_secret_word(game.secret_word),
                spy_index=game.spy_index + 1
            ),
            reply_markup=InlineKeyboardFactory.single_device_play_again_keyboard()
        )

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"finished a single-device game (game_id={game.game_id})"
        )

    @on.callback_query(SingleDevicePlayAgainAction.filter())
    async def on_play_again(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = (
                SingleDeviceGame.from_json(await state.get_value("game"))
                or await single_device_games.get_game_by_user_id(user.id)
        )

        if game is not None:
            await single_device_games.remove_game(game.game_id)

        try:
            game: SingleDeviceGame | None = await single_device_games.create_game(
                user.id,
                callback_query.from_user.id,
                game.player_amount
            )
        except Exception as e:
            await callback_query.answer()
            logger.error(
                f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
                f"Failed to create single-device game. Exception: {e}"
            )
            return

        player_index: int = 0

        await state.update_data(
            game=game.to_json(),
            player_index=player_index
        )

        await callback_query.answer()
        await user.edit_message(
            text=_("message.single_device.play.prepare").format(
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"started a single-device game (game_id={game.game_id})"
        )

    async def on_scene_leave(
            self,
            user: User,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = (
                SingleDeviceGame.from_json(await state.get_value("game"))
                or await single_device_games.get_game_by_user_id(user.id)
        )

        if game is not None:
            await single_device_games.remove_game(game.game_id)

    async def on_back(
            self,
            user: User,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = (
                SingleDeviceGame.from_json(await state.get_value("game"))
                or await single_device_games.get_game_by_user_id(user.id)
        )

        if game is not None:
            player_amount: int | None = game.player_amount
        else:
            player_amount: int | None = None

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
