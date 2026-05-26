from aiogram import Dispatcher, BaseMiddleware
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentCompileCore
from redis.asyncio import Redis

from config import config
from src.core.controllers.postgres_controller import PostgresController


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
            key_builder=DefaultKeyBuilder(
                prefix=config.default_redis_key,
                with_destiny=True,
            ),
        ),
        fsm_strategy=FSMStrategy.GLOBAL_USER,
        config=config,
        postgres=postgres,
        redis=redis,
    )

    _register_middlewares(
        dispatcher,

    )

    I18nMiddleware(
        core=FluentCompileCore(
            path="locales/{locale}",
            default_locale="en",
        ),
    ).setup(dispatcher)

    dispatcher.include_routers(

    )

    SceneRegistry(dispatcher).add(

    )

    return dispatcher
