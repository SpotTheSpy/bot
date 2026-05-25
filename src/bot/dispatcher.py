from aiogram import Dispatcher, BaseMiddleware
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.strategy import FSMStrategy
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentCompileCore

from config import config


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

    dispatcher = Dispatcher(
        fsm_strategy=FSMStrategy.GLOBAL_USER,
        config=config,
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
