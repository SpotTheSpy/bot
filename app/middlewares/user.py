from typing import Callable, Dict, Any, Awaitable, Set

from aiogram import BaseMiddleware, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User as AiogramUser, CallbackQuery

from app.controllers.users import UsersController
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import User, BotUser


class UserMiddleware(BaseMiddleware):
    def __init__(
            self,
            users: UsersController
    ) -> None:
        self._users = users

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

        state: FSMContext | None = data.get("state")
        user_json: Dict[str, Any] = await state.get_value("user")

        if user_json is not None:
            bot_user = BotUser.from_user(
                User.from_json(user_json),
                chat_id=user_json.get("chat_id"),
                message_id=user_json.get("message_id"),
                has_photo=user_json.get("has_photo"),
                bot=data.get("bot"),
                state=state
            )
        else:
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

            bot_user = BotUser.from_user(
                user,
                bot=data.get("bot"),
                state=state
            )

        if isinstance(event, CallbackQuery):
            if bot_user.chat_id is None:
                bot_user.chat_id = event.message.chat.id
            if bot_user.message_id is None:
                bot_user.message_id = event.message.message_id

        data["user"] = bot_user

        await state.update_data(user=bot_user.to_json())
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
