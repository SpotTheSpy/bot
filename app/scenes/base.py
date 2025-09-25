from abc import ABC
from typing import List, Dict, Any

from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError
from aiogram.fsm.scene import Scene
from aiogram.types import Message, InlineKeyboardMarkup, MessageEntity


class BaseScene(Scene, ABC, state="base"):
    @staticmethod
    async def edit_message(
            message: Message,
            text: str,
            entities: List[MessageEntity] | None = None,
            reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        params: Dict[str, Any] = {
            "entities": entities,
            "reply_markup": reply_markup
        }

        if entities is not None:
            params["parse_mode"] = None

        try:
            await message.edit_text(
                text,
                **params
            )
        except AiogramError:
            pass
