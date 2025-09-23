from typing import Dict, Any

from aiogram.types import TelegramObject, User
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from app.controllers.users import UsersController


class APII18nMiddleware(SimpleI18nMiddleware):
    def __init__(
            self,
            i18n: I18n,
            users: UsersController
    ) -> None:
        super().__init__(i18n)
        self._users = users

    async def get_locale(
            self,
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> str:
        user: User | None = data.get("event_from_user", None)

        if user is None:
            return self.i18n.default_locale

        locale: str | None = await self._users.get_user_locale(user.id)

        if locale is None:
            locale = await super().get_locale(event, data)
            await self._users.update_user_locale(user.id, locale)

        return locale
