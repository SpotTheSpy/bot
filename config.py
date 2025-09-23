from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    telegram_bot_token: SecretStr
    telegram_secret: SecretStr
    api_key: SecretStr

    redis_dsn: SecretStr | None = None

    base_url: str
