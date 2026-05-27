from typing import Callable, Any, Awaitable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram_i18n import I18nContext

from src.bot.exceptions.bot import BotError
from src.bot.logger import logger
from src.core.models.redis.user import User


class ErrorMiddleware(BaseMiddleware):
    """
    Handles bot errors by displaying error message to the user.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Tries to perform the handler, if a game error occurs - displays error message to the user.
        """

        try:
            return await handler(event, data)
        except BotError as e:
            user: User = data.get("user")
            i18n: I18nContext = data.get("i18n")

            await user.message.edit(i18n.get("error"))

            logger.error(
                f"{user.telegram_id} ({user.first_name}) encountered an error: {e}"
            )
