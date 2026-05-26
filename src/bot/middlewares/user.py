from typing import Callable, Any, Awaitable, Dict
from uuid import UUID

from aiogram import BaseMiddleware, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User as AiogramUser
from sqlalchemy import select, Result
from sqlalchemy.orm import joinedload

from src.core.controllers.postgres import PostgresController
from src.core.controllers.redis import RedisController
from src.core.enums.locale import Locale
from src.core.enums.time_stamp import TimeStamp
from src.core.models.postgres import User as PostgresUser, UserSettings
from src.core.models.redis.user import User as RedisUser, Message


class UserMiddleware(BaseMiddleware):
    """
    Provides user object from database on every user-related event.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Inserts user object into data. Creates a new user if necessary, never inserts None.
        """

        from_user: AiogramUser | None = data.get("event_from_user")
        if from_user is None:
            return await handler(event, data)

        state: FSMContext = data.get("state")

        user_controller: RedisController[RedisUser] = data.get("user_controller")
        if user_controller is None:
            raise ValueError("User controller instance is not set.")

        user_id: UUID | None = await self._try_get_user_id_from_state(state)

        if user_id is not None:
            user: RedisUser | None = await self._try_get_user_from_redis(user_id, user_controller)

            if user is not None:
                user.message.bot = event.bot
                data["user"] = user
                return await handler(event, data)

        postgres: PostgresController = data.get("postgres")
        if postgres is None:
            raise ValueError("PostgresController instance is not set.")

        user: PostgresUser | None = await self._try_get_user_from_postgres(from_user.id, postgres)

        if user is None:
            user: PostgresUser = await self._insert_new_user_to_postgres(
                from_user.id,
                from_user.first_name,
                Locale(from_user.language_code),
                postgres,
            )

        user: RedisUser = await self._set_user_to_redis(user, user_controller, event.bot)
        await self._set_user_id_to_state(user.id, state)

        data["user"] = user
        return await handler(event, data)

    @staticmethod
    async def _try_get_user_id_from_state(
            state: FSMContext,
    ) -> UUID | None:
        """
        Tries to get user ID from state, None if absent.

        :param state: FSMContext instance.
        :return: UUID if exists.
        """

        user_id: str | None = await state.get_value("user_id")

        if user_id is None:
            return

        try:
            return UUID(user_id)
        except ValueError:
            pass

    @staticmethod
    async def _try_get_user_from_redis(
            user_id: UUID,
            user_controller: RedisController[RedisUser],
    ) -> RedisUser | None:
        """
        Tries to get user object from redis, None if user does not exist.

        :param user_controller: User controller instance.
        :return: User object from redis.
        """

        return await user_controller.get(user_id)

    @staticmethod
    async def _try_get_user_from_postgres(
            telegram_id: int,
            postgres: PostgresController,
    ) -> PostgresUser | None:
        """
        Tries to get user object from Postgres session, None if user does not exist.

        :param telegram_id: Telegram ID.
        :param postgres: PostgresController instance.
        :return: User object from Postgres.
        """

        async with postgres.session() as session:
            result: Result = await session.execute(
                select(PostgresUser)
                .options(
                    joinedload(PostgresUser.settings),
                )
                .filter_by(telegram_id=telegram_id)
            )

            return result.scalar_one_or_none()

    @staticmethod
    async def _insert_new_user_to_postgres(
            telegram_id: int,
            first_name: str,
            locale: Locale,
            postgres: PostgresController,
    ) -> PostgresUser:
        """
        Inserts new user to Postgres.

        :param telegram_id: Telegram ID.
        :param first_name: First name.
        :param locale: Locale.
        :param postgres: PostgresController instance.
        :return: New user object.
        """

        async with postgres.session() as session:
            new_user: PostgresUser = PostgresUser(
                telegram_id=telegram_id,
                first_name=first_name,
            )
            new_user.settings = UserSettings(
                locale=locale,
            )

            session.add(new_user)
            await session.commit()

            return new_user

    @staticmethod
    async def _set_user_to_redis(
            user: PostgresUser,
            user_controller: RedisController[RedisUser],
            bot: Bot,
    ) -> RedisUser:
        """
        Sets user object to redis based on Postgres object.

        :param user: Postgres User object.
        :param user_controller: User controller instance.
        :param bot: Bot instance.
        :return: Redis User object.
        """

        new_user: RedisUser = RedisUser.new(
            user.telegram_id,
            user.first_name,
            user.settings.locale,
            Message.new(
                user.telegram_id,
                None,
                bot=bot,
            ),
        )

        await user_controller.set(new_user, expire=TimeStamp.DAY)

        return new_user

    @staticmethod
    async def _set_user_id_to_state(
            user_id: UUID,
            state: FSMContext,
    ) -> None:
        """
        Sets user ID to state.

        :param user_id: User ID.
        :param state: FSMContext instance.
        """

        await state.update_data(user_id=str(user_id))
