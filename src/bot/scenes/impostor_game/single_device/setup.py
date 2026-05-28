from typing import Dict, Any

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from config import config
from src.bot.actions.back import BackAction
from src.bot.actions.impostor_game.play import ImpostorGamePlayAction
from src.bot.actions.impostor_game.setup import (
    ImpostorGameSetupAction,
    ImpostorGameSetupPlayerAmountAction,
    ImpostorGameSetupImpostorCountAction,
)
from src.bot.keyboards.impostor_game.setup import (
    impostor_game_setup_keyboard,
    impostor_game_setup_player_count_keyboard,
    impostor_game_setup_impostor_count_keyboard,
)
from src.bot.scenes.base import BaseScene
from src.core.enums.impostor_count import ImpostorCount
from src.core.enums.impostor_game_parameter import ImpostorGameParameter
from src.core.models.redis.user import User


class SingleDeviceImpostorGameSetupScene(BaseScene, state="single_device_impostor_game_setup"):
    """
    Scene for the single device impostor game setup.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        """
        Display a setup menu for a single-device impostor game.
        """

        player_count: int = config.game_parameters.DEFAULT_PLAYER_COUNT
        impostor_count: ImpostorCount = ImpostorCount.SINGLE

        await state.update_data(
            game_parameter=None,
            player_count=player_count,
            impostor_count=impostor_count,
        )

        await user.message.edit(
            i18n.get("setup-impostor-game"),
            reply_markup=impostor_game_setup_keyboard(
                i18n,
                player_count,
                impostor_count,
            ),
        )

        await callback_query.answer()

    @on.callback_query(ImpostorGameSetupAction.filter(F.game_parameter == ImpostorGameParameter.PLAYER_COUNT))
    async def on_setup_player_count(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        player_count: int = await state.get_value("player_count")

        await user.message.edit(
            i18n.get("setup-impostor-game-player-count"),
            reply_markup=impostor_game_setup_player_count_keyboard(player_count),
        )

        await state.update_data(
            game_parameter=ImpostorGameParameter.PLAYER_COUNT,
            player_count=player_count,
        )

        await callback_query.answer()

    @on.callback_query(ImpostorGameSetupAction.filter(F.game_parameter == ImpostorGameParameter.IMPOSTOR_COUNT))
    async def on_setup_impostor_count(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        impostor_count: ImpostorCount = await state.get_value("impostor_count")

        await user.message.edit(
            i18n.get("setup-impostor-game-impostor-count"),
            reply_markup=impostor_game_setup_impostor_count_keyboard(i18n, impostor_count),
        )

        await state.update_data(
            game_parameter=ImpostorGameParameter.IMPOSTOR_COUNT,
            impostor_count=impostor_count
        )

        await callback_query.answer()

    @on.callback_query(ImpostorGameSetupPlayerAmountAction.filter())
    async def on_choose_player_count(
            self,
            callback_query: CallbackQuery,
            callback_data: ImpostorGameSetupPlayerAmountAction,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("setup-impostor-game-player-count"),
            reply_markup=impostor_game_setup_player_count_keyboard(callback_data.player_count),
        )

        await callback_query.answer()
        await state.update_data(player_count=callback_data.player_count)

    @on.callback_query(ImpostorGameSetupImpostorCountAction.filter())
    async def on_choose_impostor_count(
            self,
            callback_query: CallbackQuery,
            callback_data: ImpostorGameSetupImpostorCountAction,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("setup-impostor-game-impostor-count"),
            reply_markup=impostor_game_setup_impostor_count_keyboard(i18n, callback_data.impostor_count),
        )

        await callback_query.answer()
        await state.update_data(impostor_count=callback_data.impostor_count)

    @on.callback_query(ImpostorGamePlayAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            state: FSMContext,
    ) -> None:
        data: Dict[str, Any] = await state.get_data()

        await self.wizard.goto(
            "single_device_impostor_game_play",
            player_count=data.get("player_count"),
            impostor_count=data.get("impostor_count"),
        )

        await callback_query.answer()

    @on.callback_query.leave()
    async def on_leave(
            self,
            callback_query: CallbackQuery,
            state: FSMContext,
    ) -> None:
        await state.update_data(
            player_count=None,
            impostor_count=None,
        )

        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        data: Dict[str, Any] = await state.get_data()

        game_parameter: ImpostorGameParameter | None = data.get("game_parameter")

        if game_parameter is None:
            await self.wizard.back(user=user)
            return

        player_count: int = data.get("player_count")
        impostor_count: ImpostorCount = data.get("impostor_count")

        await user.message.edit(
            i18n.get("setup-impostor-game"),
            reply_markup=impostor_game_setup_keyboard(
                i18n,
                player_count,
                impostor_count,
            ),
        )

        await state.update_data(game_parameter=None)

        await callback_query.answer()
