from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.settings import SettingsAction
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
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
            reply_markup=InlineKeyboardFactory.single_device_settings_keyboard()
        )

    @on.callback_query(SettingsAction.filter())
    async def on_settings(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.wizard.goto("settings_single_device")

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
    pass
