from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.models.bot_user import BotUser
from app.scenes.base import BaseScene
from app.utils.inline_keyboard_factory import InlineKeyboardFactory


class MultiDeviceExplainScene(BaseScene, state="multi_device_explain"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await callback_query.answer()
        await user.edit_message(
            text=_("message.multi_device.explain"),
            reply_markup=InlineKeyboardFactory.multi_device_explain_keyboard()
        )

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
