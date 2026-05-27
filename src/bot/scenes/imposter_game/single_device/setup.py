from typing import Dict, Any

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from config import config
from src.bot.actions.back import BackAction
from src.bot.actions.imposter_game.play import ImposterGamePlayAction
from src.bot.actions.imposter_game.setup import (
    ImposterGameSetupAction,
    ImposterGameSetupPlayerAmountAction,
    ImposterGameSetupImposterCountAction,
)
from src.bot.keyboards.imposter_game.setup import (
    imposter_game_setup_keyboard,
    imposter_game_setup_player_count_keyboard,
    imposter_game_setup_imposter_count_keyboard,
)
from src.bot.scenes.base import BaseScene
from src.core.enums.imposter_count import ImposterCount
from src.core.enums.imposter_game_parameter import ImposterGameParameter
from src.core.models.redis.user import User


class SingleDeviceImposterGameSetupScene(BaseScene, state="single_device_imposter_game_setup"):
    """
    Scene for the single device imposter game setup.
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
        Display a setup menu for a single-device imposter game.
        """

        player_count: int = config.game_parameters.DEFAULT_PLAYER_COUNT
        imposter_count: ImposterCount = ImposterCount.SINGLE

        await state.update_data(
            game_parameter=None,
            player_count=player_count,
            imposter_count=imposter_count,
        )

        await user.message.edit(
            i18n.get("setup-imposter-game"),
            reply_markup=imposter_game_setup_keyboard(
                i18n,
                player_count,
                imposter_count,
            ),
        )

        await callback_query.answer()

    @on.callback_query(ImposterGameSetupAction.filter(F.game_parameter == ImposterGameParameter.PLAYER_COUNT))
    async def on_setup_player_count(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        player_count: int = await state.get_value("player_count")

        await user.message.edit(
            i18n.get("setup-imposter-game-player-count"),
            reply_markup=imposter_game_setup_player_count_keyboard(player_count),
        )

        await state.update_data(
            game_parameter=ImposterGameParameter.PLAYER_COUNT,
            player_count=player_count,
        )

        await callback_query.answer()

    @on.callback_query(ImposterGameSetupAction.filter(F.game_parameter == ImposterGameParameter.IMPOSTER_COUNT))
    async def on_setup_imposter_count(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        imposter_count: ImposterCount = await state.get_value("imposter_count")

        await user.message.edit(
            i18n.get("setup-imposter-game-imposter-count"),
            reply_markup=imposter_game_setup_imposter_count_keyboard(i18n, imposter_count),
        )

        await state.update_data(
            game_parameter=ImposterGameParameter.IMPOSTER_COUNT,
            imposter_count=imposter_count
        )

        await callback_query.answer()

    @on.callback_query(ImposterGameSetupPlayerAmountAction.filter())
    async def on_choose_player_count(
            self,
            callback_query: CallbackQuery,
            callback_data: ImposterGameSetupPlayerAmountAction,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("setup-imposter-game-player-count"),
            reply_markup=imposter_game_setup_player_count_keyboard(callback_data.player_count),
        )

        await callback_query.answer()
        await state.update_data(player_count=callback_data.player_count)

    @on.callback_query(ImposterGameSetupImposterCountAction.filter())
    async def on_choose_imposter_count(
            self,
            callback_query: CallbackQuery,
            callback_data: ImposterGameSetupImposterCountAction,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("setup-imposter-game-imposter-count"),
            reply_markup=imposter_game_setup_imposter_count_keyboard(i18n, callback_data.imposter_count),
        )

        await callback_query.answer()
        await state.update_data(imposter_count=callback_data.imposter_count)

    @on.callback_query(ImposterGamePlayAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            state: FSMContext,
    ) -> None:
        data: Dict[str, Any] = await state.get_data()

        await self.wizard.goto(
            "single_device_imposter_game_play",
            player_count=data.get("player_count"),
            imposter_count=data.get("imposter_count"),
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
            imposter_count=None,
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

        game_parameter: ImposterGameParameter | None = data.get("game_parameter")

        if game_parameter is None:
            await self.wizard.back(user=user)
            return

        player_count: int = data.get("player_count")
        imposter_count: ImposterCount = data.get("imposter_count")

        await user.message.edit(
            i18n.get("setup-imposter-game"),
            reply_markup=imposter_game_setup_keyboard(
                i18n,
                player_count,
                imposter_count,
            ),
        )

        await state.update_data(game_parameter=None)

        await callback_query.answer()
