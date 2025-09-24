from aiogram import Dispatcher
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis

from app.controllers.abstract import APIConfig
from app.controllers.single_device_games import SingleDeviceGamesController
from app.controllers.users import UsersController
from app.middlewares.i18n import APII18nMiddleware
from app.middlewares.user import UserMiddleware
from app.routes.start import start_router
from app.scenes.single_device_configure import SettingsSingleDeviceScene
from app.scenes.single_device_explain import SingleDeviceExplainScene
from app.scenes.single_device_play import SingleDevicePlayScene
from app.scenes.start import StartScene
from config import Config

config = Config(_env_file=".env")


def create_dispatcher() -> Dispatcher:
    storage: RedisStorage | None = None

    if config.redis_dsn is not None:
        redis = Redis.from_url(config.redis_dsn.get_secret_value())
        storage = RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))

    i18n = I18n(
        path="locales",
        default_locale="en",
        domain="messages"
    )
    api_config = APIConfig(
        config.base_url,
        config.api_key.get_secret_value()
    )

    users = UsersController(api_config)
    single_device_games = SingleDeviceGamesController(api_config)

    new_dispatcher = Dispatcher(
        storage=storage,
        config=config,
        users=users,
        single_device_games=single_device_games
    )

    UserMiddleware(users).setup(new_dispatcher)
    APII18nMiddleware(i18n, users).setup(new_dispatcher)

    new_dispatcher.include_routers(
        start_router
    )

    SceneRegistry(new_dispatcher).add(
        StartScene,
        SingleDeviceExplainScene,
        SettingsSingleDeviceScene,
        SingleDevicePlayScene
    )

    return new_dispatcher
