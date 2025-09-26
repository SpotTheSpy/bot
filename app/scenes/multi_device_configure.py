from typing import Set

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.multi_device_play import MultiDevicePlayAction
from app.actions.page_turn import PageTurnAction
from app.controllers.multi_device_games import MultiDeviceGamesController
from app.enums.page_turn import PageTurn
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.multi_device_game import MultiDeviceGame
from app.models.user import User
from app.parameters import Parameters
from app.scenes.base import BaseScene


class MultiDeviceConfigureScene(BaseScene, state="multi_device_configure"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            state: FSMContext
    ) -> None:
        player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT

        await state.update_data(player_amount=player_amount)

        exclude_turns: Set[PageTurn] = set()

        if player_amount <= Parameters.MIN_PLAYER_AMOUNT:
            exclude_turns.add(PageTurn.LEFT)
        if player_amount >= Parameters.MAX_PLAYER_AMOUNT:
            exclude_turns.add(PageTurn.RIGHT)

        await self.edit_message(
            callback_query.message,
            _("message.multi_device.configure").format(
                player_amount=player_amount
            ),
            reply_markup=InlineKeyboardFactory.multi_device_configure_keyboard(exclude_turns=exclude_turns)
        )

    @on.callback_query(MultiDevicePlayAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> None:
        player_amount: int | None = await state.get_value("player_amount")

        if player_amount is None:
            player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT

        game: MultiDeviceGame | None = await multi_device_games.get_game_by_user_id(user.id)

        if game is not None:
            await callback_query.answer(_("answer.multi_device_games.already_in_game"))

        game: MultiDeviceGame = await multi_device_games.create_game(
            user.id,
            player_amount
        )

        await state.update_data(game=game.to_json())

        await callback_query.answer()
        await self.wizard.goto("multi_device_play", user=user)

    @on.callback_query(PageTurnAction.filter())
    async def on_page_turn(
            self,
            callback_query: CallbackQuery,
            callback_data: PageTurnAction,
            state: FSMContext
    ) -> None:
        player_amount: int | None = await state.get_value("player_amount")

        if player_amount is None:
            player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT

        player_amount += callback_data.turn
        await state.update_data(player_amount=player_amount)

        exclude_turns: Set[PageTurn] = set()

        if player_amount <= Parameters.MIN_PLAYER_AMOUNT:
            exclude_turns.add(PageTurn.LEFT)
        if player_amount >= Parameters.MAX_PLAYER_AMOUNT:
            exclude_turns.add(PageTurn.RIGHT)

        await self.edit_message(
            callback_query.message,
            _("message.multi_device.configure").format(
                player_amount=player_amount
            ),
            reply_markup=InlineKeyboardFactory.multi_device_configure_keyboard(exclude_turns=exclude_turns)
        )

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.wizard.back()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
