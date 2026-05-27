from typing import ClassVar, Type

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class DefaultGameParameters:
    """
    Provides basic game setup parameters.
    """

    MIN_PLAYER_COUNT = 3
    """
    Minimum number of players allowed to play a game.
    """

    MAX_PLAYER_COUNT = 8
    """
    Maximum number of players allowed to play a game.
    """

    DEFAULT_PLAYER_COUNT = 4
    """
    Default number of players in game.
    """

    GUARANTEED_UNIQUE_WORD_COUNT = 30
    """
    Minimum number of guaranteed unique words before repetition in a spy game.
    """

    GUARANTEED_UNIQUE_QUESTION_COUNT = 1
    """
    Minimum number of guaranteed unique questions before repetition in an imposter game.
    """


class Config(BaseSettings):
    """
    Provides credentials for all services, telegram bot token and webhook data, etc.
    """

    TITLE: ClassVar[str] = "SpotTheSpy"

    postgres_dsn: SecretStr
    """
    DSN for database connection.
    """

    redis_dsn: SecretStr
    """
    DSN for Redis connection.
    """

    rabbitmq_dsn: SecretStr
    """
    DSN for RabbitMQ connection.
    """

    result_backend_dsn: str = "rpc://"
    """
    DSN for retrieving task results.
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

    default_redis_key: str = "spotthespy"
    """
    Default Redis object key.
    """

    game_parameters: Type[DefaultGameParameters] = DefaultGameParameters
    """
    Default game parameters.
    """


# Main Config instance.
config = Config(_env_file=".env")
