from aiogram_i18n.managers import BaseManager
from sqlalchemy import update

from src.core.controllers.postgres import PostgresController
from src.core.controllers.redis import RedisController
from src.core.enums.time_stamp import TimeStamp
from src.core.models.postgres import UserSettings
from src.core.models.redis.user import User


class LocaleManager(BaseManager):
    """
    Manager for retrieving user's locale.
    """

    def __init__(
            self,
            *,
            default_locale: str,
    ) -> None:
        """
        LocaleManager Constructor.
        :param default_locale: Default locale to use if user's locale is absent or invalid.
        """

        super().__init__(default_locale=default_locale)

    async def get_locale(
            self,
            *,
            user: User | None,
    ) -> str | None:
        """
        Retrieves locale.

        :param user: User instance.
        :return: Retrieved locale.
        """

        return user.locale

    async def set_locale(
            self,
            locale: str,
            user: User,
            postgres: PostgresController,
            user_controller: RedisController[User],
    ) -> None:
        """
        Updates locale in database.
        :param locale: New locale value.
        :param user: User instance.
        :param postgres: Postgres database session instance.
        :param user_controller: User controller instance.
        """

        user.locale = locale

        async with postgres.session() as session:
            await session.execute(
                update(UserSettings)
                .filter_by(user_id=user.id)
                .values(locale=locale)
            )
            await session.commit()

        await user_controller.set(user, expire=TimeStamp.DAY)
