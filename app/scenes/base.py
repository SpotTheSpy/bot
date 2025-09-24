from abc import ABC

from aiogram.exceptions import AiogramError
from aiogram.fsm.scene import Scene, on
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

from app.actions.back import BackAction
from app.scenes.abstract import AbstractScene


class BaseScene(Scene, AbstractScene, ABC, state="base"):
    async def on_back(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.back()

    @on.callback_query(BackAction.filter())
    async def __on_back(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.on_back(callback_query)

    @staticmethod
    async def edit_message(
            message: Message,
            text: str,
            reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        try:
            await message.edit_text(
                text,
                reply_markup=reply_markup
            )
        except AiogramError:
            pass
