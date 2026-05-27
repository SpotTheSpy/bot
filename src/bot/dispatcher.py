from aiogram import Dispatcher
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentCompileCore
from redis.asyncio import Redis

from config import config
from src.bot.locale_manager import LocaleManager
from src.bot.middlewares.error import ErrorMiddleware
from src.bot.middlewares.user import UserMiddleware
from src.bot.routes.start import start_router
from src.bot.scenes.language import LanguageScene
from src.bot.scenes.spy_game.single_device.play import SingleDeviceSpyGamePlayScene
from src.bot.scenes.spy_game.single_device.setup import SingleDeviceSpyGameSetupScene
from src.bot.scenes.spy_game.single_device.tutorial import SingleDeviceSpyGameTutorialScene
from src.bot.scenes.start import StartScene
from src.core.controllers.postgres import PostgresController
from src.core.controllers.redis import RedisController
from src.core.models.redis.imposter_game.imposter_question_queue import ImposterQuestionQueue
from src.core.models.redis.imposter_game.single_device import SingleDeviceImposterGame
from src.core.models.redis.spy_game.secret_word_queue import SecretWordQueue
from src.core.models.redis.spy_game.single_device import SingleDeviceSpyGame
from src.core.models.redis.telegram_user import TelegramUser
from src.core.models.redis.user import User


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
        single_device_spy_game_controller=RedisController[SingleDeviceSpyGame](redis),
        secret_word_controller=RedisController[SecretWordQueue](redis),
        single_device_imposter_game_controller=RedisController[SingleDeviceImposterGame](redis),
        imposter_question_controller=RedisController[ImposterQuestionQueue](redis),
    )

    dispatcher.update.outer_middleware.register(UserMiddleware())

    I18nMiddleware(
        core=FluentCompileCore(
            path="locales/{locale}",
            default_locale="en",
        ),
        manager=LocaleManager(
            default_locale="en",
        )
    ).setup(dispatcher)

    dispatcher.update.outer_middleware.register(ErrorMiddleware())

    dispatcher.include_routers(
        start_router,
    )

    SceneRegistry(dispatcher).add(
        StartScene,
        LanguageScene,
        SingleDeviceSpyGameTutorialScene,
        SingleDeviceSpyGameSetupScene,
        SingleDeviceSpyGamePlayScene,
    )

    return dispatcher
