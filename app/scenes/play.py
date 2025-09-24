from typing import Any, Dict

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.actions.next_player import NextPlayerAction
from app.actions.view_role import ViewRoleAction
from app.controllers.single_device_games import SingleDeviceGamesController
from app.enums.player_type import PlayerType
from app.exceptions.already_in_game import AlreadyInGameError
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.single_device_game import SingleDeviceGame
from app.models.user import User
from app.scenes.base import BaseScene


class PlaySingleDeviceScene(BaseScene, state="play_single_device"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            single_games: SingleDeviceGamesController
    ) -> None:
        try:
            game: SingleDeviceGame = await single_games.create_game(
                user.id,
                user.telegram_id,
                "Apple",
                4
            )
        except AlreadyInGameError:
            await callback_query.answer(_("answer.play.already_in_game"))
            await self.wizard.back()
            return

        player_index: int = 0

        await state.update_data(
            game=game.to_json(),
            player_index=player_index
        )

        await self.edit_message(
            callback_query.message,
            _("message.play.single_device.prepare").format(
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )

    @on.callback_query(ViewRoleAction.filter())
    async def on_view_role(
            self,
            callback_query: CallbackQuery,
            state: FSMContext
    ) -> None:
        data: Dict[str, Any] = await state.get_data()

        game_json: Dict[str, Any] = data.get("game")
        player_index: int = data.get("player_index")

        if game_json is None:
            return

        game: SingleDeviceGame = SingleDeviceGame.from_json(game_json)

        player_type = PlayerType.SPY if player_index == game.spy_index else PlayerType.CITIZEN

        message_text: str = {
            PlayerType.CITIZEN: _("message.play.single_device.view_role.citizen"),
            PlayerType.SPY: _("message.play.single_device.view_role.spy")
        }.get(player_type)

        await self.edit_message(
            callback_query.message,
            message_text.format(
                secret_word=game.secret_word,
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_next_player_keyboard()
        )

    @on.callback_query(NextPlayerAction.filter())
    async def on_next_player(
            self,
            callback_query: CallbackQuery,
            state: FSMContext
    ) -> None:
        data: Dict[str, Any] = await state.get_data()

        game_json: Dict[str, Any] = data.get("game")
        player_index: int = data.get("player_index")

        if game_json is None:
            return

        game: SingleDeviceGame = SingleDeviceGame.from_json(game_json)

        player_index += 1

        if player_index >= game.player_amount:
            await self.edit_message(
                callback_query.message,
                _("message.play.single_device.discuss"),
                reply_markup=InlineKeyboardFactory.single_device_finish_keyboard()
            )
            return

        await state.update_data(player_index=player_index)

        await self.edit_message(
            callback_query.message,
            _("message.play.single_device.prepare").format(
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )
