from aiogram import Dispatcher
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis

from app.controllers.api import APIConfig
from app.controllers.multi_device_games import MultiDeviceGamesController
from app.controllers.single_device_games import SingleDeviceGamesController
from app.controllers.users import UsersController
from app.controllers.redis import RedisController
from app.middlewares.i18n import UserI18nMiddleware
from app.middlewares.user import UserMiddleware
from app.models.qr_code import QRCode
from app.models.user import BotUser
from app.routes.start import start_router
from app.scenes.choose_device import ChooseDeviceScene
from app.scenes.language import LanguageScene
from app.scenes.multi_device_configure import MultiDeviceConfigureScene
from app.scenes.multi_device_explain import MultiDeviceExplainScene
from app.scenes.multi_device_play import MultiDevicePlayScene
from app.scenes.single_device_configure import SingleDeviceConfigureScene
from app.scenes.single_device_explain import SingleDeviceExplainScene
from app.scenes.single_device_play import SingleDevicePlayScene
from app.scenes.start import StartScene
from config import Config

config = Config(_env_file=".env")


def create_dispatcher() -> Dispatcher:
    redis = Redis.from_url(config.redis_dsn.get_secret_value())
    api_config = APIConfig(
        config.base_url,
        config.api_key.get_secret_value()
    )

    users = UsersController(api_config)
    single_device_games = SingleDeviceGamesController(api_config)
    multi_device_games = MultiDeviceGamesController(api_config)

    bot_users = RedisController[BotUser](redis)
    qr_codes = RedisController[QRCode](redis)

    new_dispatcher = Dispatcher(
        storage=RedisStorage(
            redis,
            key_builder=DefaultKeyBuilder(with_destiny=True)
        ),
        config=config,
        users=users,
        single_device_games=single_device_games,
        multi_device_games=multi_device_games,
        bot_users=bot_users,
        qr_codes=qr_codes
    )

    UserMiddleware(
        users,
        bot_users
    ).setup(new_dispatcher)

    UserI18nMiddleware(
        I18n(
            path="locales",
            default_locale="en",
            domain="messages"
        )
    ).setup(new_dispatcher)

    new_dispatcher.include_routers(
        start_router
    )

    SceneRegistry(new_dispatcher).add(
        StartScene,
        ChooseDeviceScene,
        LanguageScene,
        SingleDeviceExplainScene,
        SingleDeviceConfigureScene,
        SingleDevicePlayScene,
        MultiDeviceExplainScene,
        MultiDeviceConfigureScene,
        MultiDevicePlayScene
    )

    return new_dispatcher
