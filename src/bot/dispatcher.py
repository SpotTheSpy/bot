from aiogram import Dispatcher, BaseMiddleware
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentCompileCore
from redis.asyncio import Redis

from config import config
from src.bot.locale_manager import LocaleManager
from src.bot.middlewares.user import UserMiddleware
from src.bot.routes.start import start_router
from src.bot.scenes.language import LanguageScene
from src.bot.scenes.single_device_games.spy.setup import SingleDeviceSpyGameSetupScene
from src.bot.scenes.single_device_games.spy.tutorial import SingleDeviceSpyGameTutorialScene
from src.bot.scenes.start import StartScene
from src.core.controllers.postgres import PostgresController
from src.core.controllers.redis import RedisController
from src.core.models.redis.telegram_user import TelegramUser
from src.core.models.redis.user import User


def _register_middlewares(
        dispatcher: Dispatcher,
        *middlewares: BaseMiddleware,
) -> None:
    """
    Registers all middlewares as an outer middleware on a dispatcher.

    :param dispatcher: Dispatcher instance.
    :param middlewares: List of middleware instances.
    """

    for middleware in middlewares:
        dispatcher.update.outer_middleware.register(middleware)


def create_dispatcher() -> Dispatcher:
    """
    Create a Dispatcher instance for managing all requests.

    :return: Dispatcher instance.
    """

    postgres: PostgresController = PostgresController.from_dsn(config.postgres_dsn.get_secret_value())
    redis: Redis = Redis.from_url(config.redis_dsn.get_secret_value(), decode_responses=True)

    dispatcher = Dispatcher(
        storage=RedisStorage(
            redis,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        ),
        fsm_strategy=FSMStrategy.GLOBAL_USER,
        config=config,
        postgres=postgres,
        redis=redis,
        user_controller=RedisController[User](redis),
        telegram_user_controller=RedisController[TelegramUser](redis),
    )

    _register_middlewares(
        dispatcher,
        UserMiddleware(),
    )

    I18nMiddleware(
        core=FluentCompileCore(
            path="locales/{locale}",
            default_locale="en",
        ),
        manager=LocaleManager(
            default_locale="en",
        )
    ).setup(dispatcher)

    dispatcher.include_routers(
        start_router,
    )

    SceneRegistry(dispatcher).add(
        StartScene,
        LanguageScene,
        SingleDeviceSpyGameTutorialScene,
        SingleDeviceSpyGameSetupScene,
    )

    return dispatcher
