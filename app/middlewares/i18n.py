from typing import Dict, Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from app.models.bot_user import BotUser


class UserI18nMiddleware(SimpleI18nMiddleware):
    """
    Middleware from retrieving user locale from a BotUser object in workflow data.

    Must be set up after user middleware.

    If BotUser object is not specified, middleware returns locale determined by a telegram language code.
    """

    def __init__(
            self,
            i18n: I18n
    ) -> None:
        """
        Initialize middleware.

        :param i18n: I18n object to initialize simple I18n middleware.
        """

        super().__init__(i18n)

    async def get_locale(
            self,
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> str:
        """
        Retrieve locale from a BotUser object.

        :param event: Telegram event object.
        :param data: Workflow data.
        :return: Retrieved locale.
        """

        user: BotUser | None = data.get("user")

        if user is None or user.locale is None:
            locale: str = await super().get_locale(event, data)
        else:
            locale: str = user.locale

        data["locale"] = locale
        return locale
