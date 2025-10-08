import asyncio

from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery

from app.models.bot_user import BotUser
from app.scenes.base import BaseScene
from app.utils.logging import logger


class StartScene(BaseScene, state="start", reset_history_on_enter=True):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user: BotUser,
            locale: str | None = None
    ) -> None:
        await user.new_start_message(locale=locale)

        logger.info(
            f"{message.from_user.first_name} (id={message.from_user.id}) "
            f"opened the start page"
        )

        await asyncio.gather(
            user.end_single_device_game(),
            user.leave_multi_device_game(update_message=False)
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser,
            locale: str | None = None
    ) -> None:
        await user.start_message(locale=locale)
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
