from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.start import StartSingleDeviceAction
from app.controllers.single_device_games import SingleDeviceGamesController
from app.enums.game_style import GameStyle
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.single_device_game import SingleDeviceGame
from app.models.user import User
from app.scenes.base import BaseScene


class ExplainSingleDeviceScene(BaseScene, state="explain_single_device"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.edit_message(
            callback_query.message,
            _("message.explain.single_device"),
            reply_markup=InlineKeyboardFactory.play_keyboard(GameStyle.SINGLE_DEVICE)
        )

    @on.callback_query(StartSingleDeviceAction.filter())
    async def on_play(
            self,
            callback_query: CallbackQuery,
            user: User,
            single_games: SingleDeviceGamesController
    ) -> None:
        game: SingleDeviceGame = await single_games.get_game_by_user_id(user.id)

        if game is not None:
            await single_games.remove_game(game.game_id)

        await callback_query.answer()
        await self.wizard.goto("play_single_device", user=user)

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery,
            user: User
    ) -> None:
        await callback_query.answer()
        await self.wizard.back(user=user)

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()


class ExplainMultiDeviceScene(BaseScene, state="explain_multi_device"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.edit_message(
            callback_query.message,
            _("message.explain.multi_device"),
            reply_markup=InlineKeyboardFactory.play_keyboard(GameStyle.MULTI_DEVICE)
        )

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery,
            user: User
    ) -> None:
        await callback_query.answer()
        await self.wizard.back(user=user)

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
