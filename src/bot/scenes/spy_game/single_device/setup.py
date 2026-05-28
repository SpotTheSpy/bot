from typing import Dict, Any

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from config import config
from src.bot.actions.back import BackAction
from src.bot.actions.spy_game.play import SpyGamePlayAction
from src.bot.actions.spy_game.setup import (
    SpyGameSetupAction,
    SpyGameSetupPlayerAmountAction,
    SpyGameSetupCategoryAction,
    SpyGameSetupSpyCountAction,
)
from src.bot.keyboards.spy_game.setup import (
    spy_game_setup_keyboard,
    spy_game_setup_player_count_keyboard,
    spy_game_setup_category_keyboard,
    spy_game_setup_spy_count_keyboard,
)
from src.bot.scenes.base import BaseScene
from src.core.enums.spy_category import SpyCategory
from src.core.enums.spy_count import SpyCount
from src.core.enums.spy_game_parameter import SpyGameParameter
from src.core.models.redis.user import User


class SingleDeviceSpyGameSetupScene(BaseScene, state="single_device_spy_game_setup"):
    """
    Scene for the single device spy game setup.
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
        Display a setup menu for a single-device spy game.
        """

        player_count: int = config.game_parameters.DEFAULT_PLAYER_COUNT
        category: SpyCategory = SpyCategory.GENERAL
        spy_count: SpyCount = SpyCount.SINGLE

        await state.update_data(
            game_parameter=None,
            player_count=player_count,
            category=category,
            spy_count=spy_count,
        )

        await user.message.edit(
            i18n.get("setup-spy-game"),
            reply_markup=spy_game_setup_keyboard(
                i18n,
                player_count,
                category,
                spy_count,
            ),
        )

        await callback_query.answer()

    @on.callback_query(SpyGameSetupAction.filter(F.game_parameter == SpyGameParameter.PLAYER_COUNT))
    async def on_setup_player_count(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        player_count: int = await state.get_value("player_count")

        await user.message.edit(
            i18n.get("setup-spy-game-player-count"),
            reply_markup=spy_game_setup_player_count_keyboard(player_count),
        )

        await state.update_data(
            game_parameter=SpyGameParameter.PLAYER_COUNT,
            player_count=player_count,
        )

        await callback_query.answer()

    @on.callback_query(SpyGameSetupAction.filter(F.game_parameter == SpyGameParameter.CATEGORY))
    async def on_setup_category(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        category: SpyCategory = await state.get_value("category")

        await user.message.edit(
            i18n.get("setup-spy-game-category"),
            reply_markup=spy_game_setup_category_keyboard(i18n, category),
        )

        await state.update_data(
            game_parameter=SpyGameParameter.CATEGORY,
            category=category,
        )

        await callback_query.answer()

    @on.callback_query(SpyGameSetupAction.filter(F.game_parameter == SpyGameParameter.SPY_COUNT))
    async def on_setup_spy_count(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        spy_count: SpyCount = await state.get_value("spy_count")

        await user.message.edit(
            i18n.get("setup-spy-game-spy-count"),
            reply_markup=spy_game_setup_spy_count_keyboard(i18n, spy_count),
        )

        await state.update_data(
            game_parameter=SpyGameParameter.SPY_COUNT,
            spy_count=spy_count
        )

        await callback_query.answer()

    @on.callback_query(SpyGameSetupPlayerAmountAction.filter())
    async def on_choose_player_count(
            self,
            callback_query: CallbackQuery,
            callback_data: SpyGameSetupPlayerAmountAction,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("setup-spy-game-player-count"),
            reply_markup=spy_game_setup_player_count_keyboard(callback_data.player_count),
        )

        await callback_query.answer()
        await state.update_data(player_count=callback_data.player_count)

    @on.callback_query(SpyGameSetupCategoryAction.filter())
    async def on_choose_category(
            self,
            callback_query: CallbackQuery,
            callback_data: SpyGameSetupCategoryAction,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("setup-spy-game-category"),
            reply_markup=spy_game_setup_category_keyboard(i18n, callback_data.category),
        )

        await callback_query.answer()
        await state.update_data(category=callback_data.category)

    @on.callback_query(SpyGameSetupSpyCountAction.filter())
    async def on_choose_spy_count(
            self,
            callback_query: CallbackQuery,
            callback_data: SpyGameSetupSpyCountAction,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("setup-spy-game-spy-count"),
            reply_markup=spy_game_setup_spy_count_keyboard(i18n, callback_data.spy_count),
        )

        await callback_query.answer()
        await state.update_data(spy_count=callback_data.spy_count)

    @on.callback_query(SpyGamePlayAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            state: FSMContext,
    ) -> None:
        data: Dict[str, Any] = await state.get_data()

        await self.wizard.goto(
            "single_device_spy_game_play",
            player_count=data.get("player_count"),
            category=data.get("category"),
            spy_count=data.get("spy_count"),
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
            category=None,
            spy_count=None,
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

        game_parameter: SpyGameParameter | None = data.get("game_parameter")

        if game_parameter is None:
            await self.wizard.back(user=user)
            return

        player_count: int = data.get("player_count")
        category: SpyCategory = data.get("category")
        spy_count: SpyCount = data.get("spy_count")

        await user.message.edit(
            i18n.get("setup-spy-game"),
            reply_markup=spy_game_setup_keyboard(
                i18n,
                player_count,
                category,
                spy_count,
            ),
        )

        await state.update_data(game_parameter=None)

        await callback_query.answer()
