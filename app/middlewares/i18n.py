from typing import Dict, Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from app.models.user import BotUser


class UserI18nMiddleware(SimpleI18nMiddleware):
    def __init__(
            self,
            i18n: I18n
    ) -> None:
        super().__init__(i18n)

    async def get_locale(
            self,
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> str:
        user: BotUser | None = data.get("user")

        if user is None or user.locale is None:
            locale: str = await super().get_locale(event, data)
        else:
            locale: str = user.locale

        data["locale"] = locale
        return locale
