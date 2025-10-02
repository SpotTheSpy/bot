from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.multi_device_enter import MultiDeviceEnter
from app.actions.single_device_enter import SingleDeviceEnter
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.models.user import User
from app.scenes.base import BaseScene


class ChooseDeviceScene(BaseScene, state="choose_device"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.edit_message(
            callback_query.message,
            _("message.choose_device"),
            reply_markup=InlineKeyboardFactory.choose_device_keyboard()
        )

    @on.callback_query(SingleDeviceEnter.filter())
    async def on_single_device_enter(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.goto("single_device_explain")

    @on.callback_query(MultiDeviceEnter.filter())
    async def on_multi_device_enter(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.goto("multi_device_explain")

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery,
            user: User
    ) -> None:
        await self.wizard.back()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
