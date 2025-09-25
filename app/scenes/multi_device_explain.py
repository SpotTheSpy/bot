from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.multi_device_configure import MultiDeviceConfigureAction
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.scenes.base import BaseScene


class MultiDeviceExplainScene(BaseScene, state="multi_device_explain"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.edit_message(
            callback_query.message,
            _("message.multi_device.explain"),
            reply_markup=InlineKeyboardFactory.multi_device_explain_keyboard()
        )

    @on.callback_query(MultiDeviceConfigureAction.filter())
    async def on_configure(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.wizard.goto("multi_device_configure")

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
