from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.actions.single_device_enter import SingleDeviceEnter
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.models.user import User
from app.scenes.base import BaseScene


class StartScene(BaseScene, state="start", reset_data_on_enter=True, reset_history_on_enter=True):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user: User
    ) -> None:
        await message.delete()

        await message.answer(
            _("message.start.main").format(
                first_name=user.first_name
            ),
            reply_markup=InlineKeyboardFactory.start_keyboard()
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: User
    ) -> None:
        await self.edit_message(
            callback_query.message,
            _("message.start.main").format(
                first_name=user.first_name
            ),
            reply_markup=InlineKeyboardFactory.start_keyboard()
        )

    @on.callback_query(SingleDeviceEnter.filter())
    async def on_single_device_enter(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.wizard.goto("single_device_explain")

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
