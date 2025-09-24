from abc import ABC

from aiogram.exceptions import AiogramError
from aiogram.fsm.scene import Scene
from aiogram.types import Message, InlineKeyboardMarkup


class BaseScene(Scene, ABC, state="base"):
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
