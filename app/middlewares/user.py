from typing import Callable, Dict, Any, Awaitable, Set
from uuid import UUID

from aiogram import BaseMiddleware, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User as AiogramUser, CallbackQuery

from app.controllers.users import UsersController
from app.controllers.redis import RedisController
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import User, BotUser


class UserMiddleware(BaseMiddleware):
    def __init__(
            self,
            users: UsersController,
            bot_users: RedisController[BotUser]
    ) -> None:
        self._users = users
        self._bot_users = bot_users

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        from_user: AiogramUser | None = data.get("event_from_user")

        if from_user is None:
            data["user"] = None
            return await handler(event, data)

        state: FSMContext = data.get("state")

        try:
            user_id = UUID(await state.get_value("user_id"))

            bot_user: BotUser | None = await self._bot_users.get(
                user_id,
                bot=data.get("bot"),
                from_json_method=BotUser.from_json_and_controller_and_bot
            )
        except (TypeError, ValueError):
            bot_user = None

        if bot_user is None:
            user: User | None = await self._users.get_user(from_user.id)

            if user is None:
                try:
                    user: User = await self._users.create_user(
                        from_user.id,
                        from_user.first_name,
                        from_user.username,
                        from_user.language_code
                    )
                except AlreadyExistsError:
                    data["user"] = None
                    return await handler(event, data)

            bot_user = BotUser.from_json_and_controller_and_bot(
                user.to_json(),
                bot=data.get("bot"),
                controller=self._bot_users
            )

            await state.update_data(user_id=str(bot_user.id))

        update_bot_user: bool = False

        if isinstance(event, CallbackQuery):
            if bot_user.chat_id is None:
                update_bot_user: bool = True
                bot_user.chat_id = event.message.chat.id
            if bot_user.message_id is None:
                update_bot_user: bool = True
                bot_user.message_id = event.message.message_id

        if update_bot_user:
            await bot_user.save()

        data["user"] = bot_user
        return await handler(event, data)

    def setup(
            self,
            router: Router,
            exclude: Set[str] | None = None
    ) -> None:
        if exclude is None:
            exclude = set()

        exclude_events = {"update", *exclude}

        for event_name, observer in router.observers.items():
            if event_name in exclude_events:
                continue
            observer.outer_middleware(self)
