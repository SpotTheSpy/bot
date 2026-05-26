from typing import Any
from uuid import UUID

from aiogram import Bot
from uuid_extensions import uuid7

from src.core.enums.locale import Locale
from src.core.models.abstract import AbstractModel
from src.core.models.redis.base import RedisModel


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
        return cls(
            chat_id=chat_id,
            message_id=message_id,
            _bot=bot,
        )

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


class User(RedisModel):
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

    @classmethod
    def new(
            cls,
            telegram_id: int,
            first_name: str,
            locale: Locale,
            message: Message,
    ) -> "User":
        return cls(
            id=uuid7(),
            telegram_id=telegram_id,
            first_name=first_name,
            locale=locale,
            message=message,
        )

    @property
    def primary_key(self) -> UUID:
        """
        Returns user's ID.

        :return: User's ID.
        """

        return self.id
