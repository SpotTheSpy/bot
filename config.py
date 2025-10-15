from typing import ClassVar

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Main config class.

    Provides access credentials for all services.
    """

    TITLE: ClassVar[str] = "SpotTheSpy"
    """
    Application title.
    """

    telegram_bot_token: SecretStr
    """
    Telegram bot token.
    """

    telegram_secret: SecretStr | None = None
    """
    Telegram bot secret used to authenticating Telegram webhook (Required only if webhook is used).
    """

    webhook_url: str | None = None
    """
    Base webhook URL by which telegram will send updates (Required only if webhook is used).
    """

    webhook_path: str | None = None
    """
    URL path by which telegram will send updates (Required only if webhook is used).
    """

    api_key: SecretStr
    """
    API-Key for authenticating in a Back-End services
    """

    api_url: str
    """
    Base Back-End ASGI URL (Usually http://localhost:8000/v1).
    """

    redis_dsn: SecretStr
    """
    DSN for Redis connection.
    """
