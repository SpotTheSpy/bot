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

    min_player_amount: int = 3
    """
    Minimum player count in any game.
    """

    max_player_amount: int = 8
    """
    Maximum player count in any game.
    """

    default_player_amount: int = 4
    """
    Default player count in any game.
    """

    api_retry_cycles: int = 3
    """
    Number of times to retry API calls if the ASGI server is temporarily unavailable.
    """

    api_retry_timeout: int = 1
    """
    Timeout in seconds between retrying API calls.
    """

    telegram_bot_start_url: str
    """
    Telegram bot URL template used to generate a bot deeplink.
    """

    default_redis_key: str = "spotthespy"
    """
    Default prefix for all Redis keys managed by Redis controllers.
    """

    default_blurred_qr_code_key: str = "blurred"
    """
    Default Redis key for blurred QR-Code file ID.
    """


# Main Config instance.
config = Config(_env_file=".env")
