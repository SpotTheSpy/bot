from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.actions.choose_device import ChooseDeviceAction
from app.actions.language import LanguageAction
from app.controllers.multi_device_games import MultiDeviceGamesController
from app.controllers.single_device_games import SingleDeviceGamesController
from app.models.user import BotUser
from app.scenes.base import BaseScene
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.utils.logging import logger


class StartScene(BaseScene, state="start", reset_data_on_enter=True, reset_history_on_enter=True):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user: BotUser,
            single_device_games: SingleDeviceGamesController,
            multi_device_games: MultiDeviceGamesController,
            locale: str | None = None
    ) -> None:
        await user.new_message(
            message.chat.id,
            message.message_id,
            text=_("message.start", locale=locale),
            reply_markup=InlineKeyboardFactory.start_keyboard(locale)
        )

        await single_device_games.remove_game_by_user_id(user.id)
        await multi_device_games.remove_game_by_user_id(user.id)

        logger.info(
            f"{message.from_user.first_name} (id={message.from_user.id}) "
            f"opened the start page"
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            locale: str | None = None
    ) -> None:
        await callback_query.answer()
        await user.edit_message(
            text=_("message.start", locale=locale),
            reply_markup=InlineKeyboardFactory.start_keyboard(locale)
        )

    @on.callback_query(ChooseDeviceAction.filter())
    async def on_choose_device(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.goto("choose_device")

    @on.callback_query(LanguageAction.filter())
    async def on_language(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await self.wizard.goto("language", user=user)

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
