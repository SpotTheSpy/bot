from typing import Set

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.page_turn import PageTurnAction
from app.actions.start import StartSingleDeviceAction
from app.controllers.single_device_games import SingleDeviceGamesController
from app.enums.page_turn import PageTurn
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.single_device_game import SingleDeviceGame
from app.models.user import User
from app.scenes.base import BaseScene


class SettingsSingleDeviceScene(BaseScene, state="settings_single_device"):
    _MIN_PLAYER_AMOUNT: int = 3
    _MAX_PLAYER_AMOUNT: int = 8
    _DEFAULT_PLAYER_AMOUNT: int = 4

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            state: FSMContext
    ) -> None:
        player_amount: int = self._DEFAULT_PLAYER_AMOUNT

        await state.update_data(player_amount=player_amount)

        exclude_turns: Set[PageTurn] = set()

        if player_amount <= self._MIN_PLAYER_AMOUNT:
            exclude_turns.add(PageTurn.LEFT)
        if player_amount >= self._MAX_PLAYER_AMOUNT:
            exclude_turns.add(PageTurn.RIGHT)

        await self.edit_message(
            callback_query.message,
            _("message.play.single_device.configure").format(
                player_amount=player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_play_keyboard(exclude_turns=exclude_turns)
        )

    @on.callback_query(StartSingleDeviceAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            single_games: SingleDeviceGamesController
    ) -> None:
        player_amount: int | None = await state.get_value("player_amount")

        if player_amount is None:
            player_amount: int = self._DEFAULT_PLAYER_AMOUNT

        game: SingleDeviceGame | None = await single_games.get_game_by_user_id(user.id)

        if game is not None:
            await single_games.remove_game(game.game_id)

        game: SingleDeviceGame = await single_games.create_game(
            user.id,
            user.telegram_id,
            player_amount
        )

        await state.update_data(game=game.to_json())

        await callback_query.answer()
        await self.wizard.goto("play_single_device")

    @on.callback_query(PageTurnAction.filter())
    async def on_page_turn(
            self,
            callback_query: CallbackQuery,
            callback_data: PageTurnAction,
            state: FSMContext
    ) -> None:
        player_amount: int | None = await state.get_value("player_amount")

        if player_amount is None:
            player_amount: int = self._DEFAULT_PLAYER_AMOUNT

        player_amount += callback_data.turn
        await state.update_data(player_amount=player_amount)

        exclude_turns: Set[PageTurn] = set()

        if player_amount <= self._MIN_PLAYER_AMOUNT:
            exclude_turns.add(PageTurn.LEFT)
        if player_amount >= self._MAX_PLAYER_AMOUNT:
            exclude_turns.add(PageTurn.RIGHT)

        await self.edit_message(
            callback_query.message,
            _("message.play.single_device.configure").format(
                player_amount=player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_play_keyboard(exclude_turns=exclude_turns)
        )

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
