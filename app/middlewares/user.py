from typing import Callable, Dict, Any, Awaitable, Set

from aiogram import BaseMiddleware, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User as AiogramUser

from app.controllers.users import UsersController
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import User


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
        data["user"] = None

        from_user: AiogramUser | None = data.get("event_from_user")
        if from_user is None:
            return await handler(event, data)

        state: FSMContext | None = data.get("state")
        user_json: Dict[str, Any] = await state.get_value("user")

        if user_json is not None:
            data["user"] = User.from_dict(user_json)
            return await handler(event, data)

        user: User | None = await self._users.get_user(from_user.id)

        if user is None:
            try:
                user = await self._users.create_user(
                    from_user.id,
                    from_user.first_name,
                    from_user.username,
                    from_user.language_code
                )
            except AlreadyExistsError:
                return await handler(event, data)

        data["user"] = user
        await state.update_data(user=user.model_dump())
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
