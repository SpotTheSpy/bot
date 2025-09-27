from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.menu import MenuAction
from app.actions.single_device_finish import SingleDeviceFinishAction
from app.actions.single_device_play_again import SingleDevicePlayAgainAction
from app.actions.single_device_proceed import SingleDeviceProceedPlayerAction
from app.actions.single_device_view_role import SingleDeviceViewRoleAction
from app.controllers.single_device_games import SingleDeviceGamesController
from app.data.secret_words_controller import SecretWordsController
from app.enums.player_role import PlayerRole
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.single_device_game import SingleDeviceGame
from app.models.user import User
from app.scenes.base import BaseScene


class SingleDevicePlayScene(BaseScene, state="single_device_play"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            player_amount: int,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame = await single_device_games.create_game(
            user.id,
            callback_query.from_user.id,
            player_amount
        )

        player_index: int = 0

        await state.update_data(
            game=game.to_json(),
            player_index=player_index
        )

        await self.edit_message(
            callback_query.message,
            _("message.single_device.play.prepare").format(
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )

    @on.callback_query(SingleDeviceViewRoleAction.filter())
    async def on_view_role(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = await SingleDeviceGame.from_context(
            user.id,
            state,
            single_device_games
        )
        player_index: int = await state.get_value("player_index")

        role = PlayerRole.SPY if player_index == game.spy_index else PlayerRole.CITIZEN

        message_text: str = {
            PlayerRole.CITIZEN: _("message.single_device.play.view_role.citizen"),
            PlayerRole.SPY: _("message.single_device.play.view_role.spy")
        }.get(role)

        await self.edit_message(
            callback_query.message,
            message_text.format(
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
            user: User,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = await SingleDeviceGame.from_context(
            user.id,
            state,
            single_device_games
        )
        player_index: int = await state.get_value("player_index")

        player_index += 1

        if player_index >= game.player_amount:
            await self.edit_message(
                callback_query.message,
                _("message.single_device.play.discuss"),
                reply_markup=InlineKeyboardFactory.single_device_finish_keyboard()
            )
            return

        await state.update_data(player_index=player_index)

        await self.edit_message(
            callback_query.message,
            _("message.single_device.play.prepare").format(
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )

    @on.callback_query(SingleDeviceFinishAction.filter())
    async def on_finish(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = await SingleDeviceGame.from_context(
            user.id,
            state,
            single_device_games
        )

        await self.edit_message(
            callback_query.message,
            _("message.single_device.play.finish").format(
                secret_word=SecretWordsController.get_secret_word(game.secret_word),
                spy_index=game.spy_index + 1
            ),
            reply_markup=InlineKeyboardFactory.single_device_play_again_keyboard()
        )

    @on.callback_query(SingleDevicePlayAgainAction.filter())
    async def on_play_again(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = await SingleDeviceGame.from_context(
            user.id,
            state,
            single_device_games
        )

        await single_device_games.remove_game(game.game_id)

        game: SingleDeviceGame = await single_device_games.create_game(
            user.id,
            callback_query.from_user.id,
            game.player_amount
        )

        player_index: int = 0

        await state.update_data(
            game=game.to_json(),
            player_index=player_index
        )

        await self.edit_message(
            callback_query.message,
            _("message.single_device.play.prepare").format(
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )

    @on.callback_query.leave()
    async def on_leave(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = await SingleDeviceGame.from_context(
            user.id,
            state,
            single_device_games
        )

        await single_device_games.remove_game(game.game_id)

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
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame | None = await SingleDeviceGame.from_context(
            user.id,
            state,
            single_device_games
        )

        await callback_query.answer()
        await self.wizard.back(player_amount=game.player_amount)

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
