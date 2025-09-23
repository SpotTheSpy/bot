from aiogram import Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import Config

config = Config(_env_file=".env")


def create_dispatcher() -> Dispatcher:
    storage: RedisStorage | None = None

    if config.redis_dsn is not None:
        redis = Redis.from_url(config.redis_dsn.get_secret_value())
        storage = RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))

    new_dispatcher = Dispatcher(
        storage=storage,
        config=config
    )

    return new_dispatcher
