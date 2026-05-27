import asyncio
from typing import List, Coroutine
from uuid import UUID

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions
from aiogram.types import Message as AiogramMessage
from uuid_extensions import uuid7

from src.bot.logger import logger
from src.core.enums.locale import Locale
from src.core.models.abstract import AbstractModel
from src.core.models.redis.abstract import AbstractRedisModel


class Message(AbstractModel):
    """
    Represents a message sent by the bot with which user is currently interacting.
    """

    chat_id: int
    """
    Message chat ID.
    """

    message_id: int | None = None
    """
    Message ID.
    """

    _bot: Bot | None = None
    """
    Bot instance. Must be set on/after initialization.
    """

    @classmethod
    def new(
            cls,
            chat_id: int,
            message_id: int | None = None,
            *,
            bot: Bot,
    ) -> "Message":
        new_message: Message = cls(
            chat_id=chat_id,
            message_id=message_id,
        )

        new_message.bot = bot
        return new_message

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            raise ValueError("Bot instance is not initialized.")

        return self._bot

    @bot.setter
    def bot(
            self,
            value: Bot,
    ) -> None:
        if self._bot is not None:
            raise ValueError("Bot instance is already initialized.")

        self._bot = value

    async def replace(
            self,
            text: str,
            *,
            reply_markup: InlineKeyboardMarkup | None = None,
            message_to_delete: int | None = None,
    ) -> None:
        """
        Replace a message with a new one.

        :param text: Text of the message.
        :param reply_markup: Reply markup.
        :param message_to_delete: Message ID which should be deleted alongside with an old message,
        usually a user's command.
        """

        coroutines: List[Coroutine] = [
            self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                reply_markup=reply_markup,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            ),
            self.bot.delete_message(
                self.chat_id,
                self.message_id
            ),
        ]

        if message_to_delete is not None:
            coroutines.append(
                self.bot.delete_message(
                    self.chat_id,
                    message_to_delete
                )
            )

        new_message, *_ = await asyncio.gather(*coroutines, return_exceptions=True)

        if not isinstance(new_message, AiogramMessage):
            if isinstance(new_message, (TelegramBadRequest, ValueError)):
                logger.warning(
                    f"{self.chat_id} ({self.message_id}) Error while replacing message: {new_message}."
                )
            return

        self.message_id = new_message.message_id

    async def edit(
            self,
            text: str,
            *,
            reply_markup: InlineKeyboardMarkup | None = None,
            message_to_delete: int | None = None,
    ) -> None:
        """
        Edit a message. Replaces old one if fails.

        :param text: Text of the message.
        :param reply_markup: Reply markup.
        :param message_to_delete: Message ID which should be deleted alongside with an old message,
        if editing fails.
        """

        try:
            if self.message_id is None:
                raise ValueError

            coroutines: List[Coroutine] = [
                self.bot.edit_message_text(
                    chat_id=self.chat_id,
                    message_id=self.message_id,
                    text=text,
                    reply_markup=reply_markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                ),
            ]

            if message_to_delete is not None:
                coroutines.append(
                    self.bot.delete_message(
                        self.chat_id,
                        message_to_delete,
                    ),
                )

            result, *_ = await asyncio.gather(*coroutines, return_exceptions=True)

            if isinstance(result, Exception):
                raise result
        except (TelegramBadRequest, ValueError) as error:
            if isinstance(error, TelegramBadRequest) and "message is not modified" in error.message:
                return

            logger.warning(
                f"{self.chat_id} ({self.message_id}) Error while editing message: {error}. Trying to replace..."
            )

            await self.replace(
                text,
                reply_markup=reply_markup,
                message_to_delete=message_to_delete,
            )


class ActiveGames(AbstractModel):
    """
    Represents user's active games.
    """

    active_single_device_spy_game: UUID | None = None
    """
    ID of user's active single device spy game.
    """

    active_single_device_impostor_game: UUID | None = None

    @classmethod
    def new(
            cls,
            *,
            active_single_device_spy_game: UUID | None = None,
            active_single_device_impostor_game: UUID | None = None,
    ) -> "ActiveGames":
        return cls(
            active_single_device_spy_game=active_single_device_spy_game,
            active_single_device_impostor_game=active_single_device_impostor_game,
        )


class User(AbstractRedisModel):
    """
    Represents a user which is currently using bot.
    """

    id: UUID
    """
    User ID.
    """

    telegram_id: int
    """
    Telegram ID.
    """

    first_name: str
    """
    First name from telegram.
    """

    locale: Locale
    """
    User's chosen locale.
    """

    message: Message
    """
    Message sent by the bot with which user is currently interacting.
    """

    active_games: ActiveGames
    """
    A set of active games IDs.
    """

    @classmethod
    def new(
            cls,
            telegram_id: int,
            first_name: str,
            locale: Locale,
            message: Message,
            *,
            user_id: UUID | None = None,
            active_games: ActiveGames | None = None,
    ) -> "User":
        return cls(
            id=user_id or uuid7(),
            telegram_id=telegram_id,
            first_name=first_name,
            locale=locale,
            message=message,
            active_games=active_games or ActiveGames.new(),
        )

    @classmethod
    def key(cls) -> str:
        return "user"

    @property
    def primary_key(self) -> UUID:
        """
        Returns user's ID.

        :return: User's ID.
        """

        return self.id
