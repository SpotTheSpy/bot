from abc import ABC
from typing import List, Dict, Any

from aiogram.exceptions import AiogramError
from aiogram.fsm.scene import Scene
from aiogram.types import Message, InlineKeyboardMarkup, MessageEntity, InputFile, InputMediaPhoto


class BaseScene(Scene, ABC, state="base"):
    @staticmethod
    async def edit_message(
            message: Message,
            text: str | None = None,
            photo: str | InputFile | None = None,
            entities: List[MessageEntity] | None = None,
            reply_markup: InlineKeyboardMarkup | None = None,
            only_edit_caption: bool = False
    ) -> Message | None:
        params: Dict[str, Any] = {
            "entities": entities,
            "caption_entities": entities,
            "reply_markup": reply_markup
        }

        if entities is not None:
            params["parse_mode"] = None

        try:
            if photo is None:
                if only_edit_caption:
                    if message.photo is not None:
                        return await message.edit_caption(caption=text, **params)
                else:
                    if message.photo is None:
                        return await message.edit_text(text, **params)
                    else:

                        new_message: Message = await message.answer(text, **params)
                        await message.delete()
                        return new_message
            else:
                if message.photo is not None:
                    return await message.edit_media(InputMediaPhoto(media=photo, caption=text, **params), **params)
                else:
                    new_message: Message = await message.answer_photo(photo, caption=text, **params)
                    await message.delete()
                    return new_message
        except AiogramError:
            return
