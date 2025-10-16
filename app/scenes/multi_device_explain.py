from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message

from app.models.bot_user import BotUser
from app.scenes.base import BaseScene


class MultiDeviceExplainScene(BaseScene, state="multi_device_explain"):
    """
    Scene for explanation how to play a multi-device game.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.explain_multi_device()
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
