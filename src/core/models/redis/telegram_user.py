from typing import ClassVar
from uuid import UUID

from src.core.models.redis.base import RedisModel


class TelegramUser(RedisModel):
    key: ClassVar[str] = "telegram_user"
    """
    Unique key for telegram user models.
    """

    telegram_id: int
    """
    Telegram ID.
    """

    user_id: UUID
    """
    User ID.
    """

    @classmethod
    def new(
            cls,
            telegram_id: int,
            user_id: UUID,
    ) -> "TelegramUser":
        return cls(
            telegram_id=telegram_id,
            user_id=user_id,
        )

    @property
    def primary_key(self) -> int:
        """
        Returns user's telegram ID.

        :return: Telegram ID.
        """

        return self.telegram_id
