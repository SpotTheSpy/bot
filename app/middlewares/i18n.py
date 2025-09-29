from typing import Dict, Any

from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from app.controllers.users import UsersController
from app.models.user import User


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
        user: User | None = data.get("user")

        if user is None:
            return self.i18n.default_locale

        state: FSMContext = data.get("state")

        locale: str | None = await state.get_value("locale")

        if locale is None:
            locale = await self._users.get_user_locale(user.id)

            if locale is None:
                locale: str = await super().get_locale(event, data)
                await self._users.update_user_locale(user.id, locale)

            await state.update_data(locale=locale)

        data["locale"] = locale
        return locale
