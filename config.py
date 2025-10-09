from typing import ClassVar

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    title: ClassVar[str] = "SpotTheSpy"

    telegram_bot_token: SecretStr
    telegram_secret: SecretStr

    api_key: SecretStr
    base_url: str

    redis_dsn: SecretStr
