import logging
from datetime import datetime
from typing import Dict, Any, List, TYPE_CHECKING
from uuid import UUID

from aiogram import Bot
from aiogram.exceptions import AiogramError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputFile, MessageEntity, InlineKeyboardMarkup, InputMediaPhoto
from pydantic import ValidationError

from app.models.abstract import AbstractModel

if TYPE_CHECKING:
    from app.controllers.redis.bot_users import BotUsersController
else:
    BotUsersController = Any


class User(AbstractModel):
    id: UUID
    telegram_id: int
    first_name: str
    username: str | None
    locale: str | None
    created_at: datetime
    updated_at: datetime | None


class BotUser(User, arbitrary_types_allowed=True):
    chat_id: int | None = None
    message_id: int | None = None
    has_photo: bool | None = None

    bot: Bot | None = None
    controller: BotUsersController | None = None

    @classmethod
    def from_user(
            cls,
            user: User,
            chat_id: int | None = None,
            message_id: int | None = None,
            has_photo: bool | None = None,
            bot: Bot | None = None,
            controller: BotUsersController | None = None
    ) -> 'BotUser':
        return cls(
            **user.model_dump(),
            chat_id=chat_id,
            message_id=message_id,
            has_photo=has_photo,
            bot=bot,
            controller=controller
        )

    def to_json(self) -> Dict[str, Any] | None:
        try:
            return self.model_dump(mode="json", exclude={"bot", "controller"})
        except ValidationError:
            pass

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

    async def save(self) -> None:
        await self.controller.set_bot_user(self)


class CreateUser(AbstractModel):
    telegram_id: int
    first_name: str
    username: str | None
    locale: str | None = None
