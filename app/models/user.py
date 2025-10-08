import logging
from datetime import datetime
from typing import Dict, Any, List, Self, ClassVar
from uuid import UUID

from aiogram import Bot
from aiogram.exceptions import AiogramError
from aiogram.types import Message, InputFile, MessageEntity, InlineKeyboardMarkup, InputMediaPhoto
from pydantic import BaseModel

from app.controllers.redis import RedisController
from app.models.abstract import AbstractModel
from app.models.redis import AbstractRedisModel


class User(AbstractModel):
    id: UUID
    telegram_id: int
    first_name: str
    username: str | None
    locale: str | None
    created_at: datetime
    updated_at: datetime | None

    @property
    def primary_key(self) -> Any:
        return self.id


class BotUser(User, AbstractRedisModel, arbitrary_types_allowed=True):
    key: ClassVar[str] = "bot_user"

    chat_id: int | None = None
    message_id: int | None = None
    has_photo: bool | None = None

    _bot: Bot | None = None

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            raise ValueError("Bot is not set")
        return self._bot

    @classmethod
    def from_json_and_controller_and_bot(
            cls,
            data: Dict[str, Any],
            *,
            bot: Bot | None = None,
            controller: RedisController[Self] | None = None,
            **kwargs: Any
    ) -> Self | None:
        user = cls.from_json(data, **kwargs)

        if user is not None:
            user._controller = controller
            user._bot = bot

        return user

    async def new_message(
            self,
            chat_id: int,
            text: str | None = None,
            photo: str | InputFile | None = None,
            entities: List[MessageEntity] | None = None,
            reply_markup: InlineKeyboardMarkup | None = None
    ) -> Message | None:
        if chat_id is not None:
            self.chat_id = chat_id

        params: Dict[str, Any] = {
            "entities": entities,
            "reply_markup": reply_markup
        }

        if entities is not None:
            params["parse_mode"] = None

        try:
            if photo is None:
                new_message: Message = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    **params
                )
                if self.message_id is not None:
                    await self.bot.delete_message(
                        self.chat_id,
                        self.message_id
                    )
            else:
                params["caption_entities"] = params.pop("entities")

                new_message: Message = await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=text,
                    **params
                )
                if self.message_id is not None:
                    await self.bot.delete_message(
                        self.chat_id,
                        self.message_id
                    )
        except AiogramError:
            return
        else:
            self.chat_id = new_message.chat.id
            self.message_id = new_message.message_id
            self.has_photo = new_message.photo is not None

            await self.save()
            return new_message

    async def edit_message(
            self,
            chat_id: int | None = None,
            message_id: int | None = None,
            text: str | None = None,
            photo: str | InputFile | None = None,
            entities: List[MessageEntity] | None = None,
            reply_markup: InlineKeyboardMarkup | None = None,
            only_edit_caption: bool = False
    ) -> Message | None:
        if chat_id is not None:
            self.chat_id = chat_id
        elif self.chat_id is None:
            return

        if message_id is not None:
            self.message_id = message_id
        elif self.message_id is None:
            return

        params: Dict[str, Any] = {
            "entities": entities,
            "reply_markup": reply_markup
        }

        if entities is not None:
            params["parse_mode"] = None

        try:
            if photo is None:
                if only_edit_caption:
                    if self.has_photo:
                        params["caption_entities"] = params.pop("entities")

                        new_message: Message = await self.bot.edit_message_caption(
                            chat_id=self.chat_id,
                            message_id=self.message_id,
                            caption=text,
                            **params
                        )
                    else:
                        return
                else:
                    if not self.has_photo:
                        new_message: Message = await self.bot.edit_message_text(
                            chat_id=self.chat_id,
                            message_id=self.message_id,
                            text=text,
                            **params
                        )
                    else:
                        new_message: Message = await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=text,
                            **params
                        )
                        await self.bot.delete_message(
                            self.chat_id,
                            self.message_id
                        )
            else:
                if self.has_photo:
                    params["caption_entities"] = params.pop("entities")
                    params.pop("reply_markup")

                    new_message: Message = await self.bot.edit_message_media(
                        chat_id=self.chat_id,
                        message_id=self.message_id,
                        media=InputMediaPhoto(
                            media=photo,
                            caption=text,
                            **params
                        ),
                        reply_markup=reply_markup
                    )
                else:
                    params["caption_entities"] = params.pop("entities")

                    new_message: Message = await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=photo,
                        caption=text,
                        **params
                    )
                    await self.bot.delete_message(
                        self.chat_id,
                        self.message_id
                    )
        except AiogramError as e:
            logging.exception(e)
            return

        self.chat_id = new_message.chat.id
        self.message_id = new_message.message_id
        self.has_photo = new_message.photo is not None

        await self.save()
        return new_message

    async def save(self) -> None:
        await self.controller.set(self)


class CreateUser(BaseModel):
    telegram_id: int
    first_name: str
    username: str | None
    locale: str | None = None


class UpdateUser(BaseModel):
    telegram_id: int | None = None
    first_name: str | None = None
    username: str | None = None
    locale: str | None = None
