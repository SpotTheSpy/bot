from typing import Callable, Dict, Any, Awaitable, Set
from uuid import UUID

from aiogram import BaseMiddleware, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User as AiogramUser, CallbackQuery, Chat

from app.controllers.redis import RedisController
from app.controllers.users import UsersController
from app.exceptions.already_exists import AlreadyExistsError
from app.models.bot_user import BotUser
from app.models.user import User


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
        chat: Chat | None = data.get("event_chat")

        if from_user is None:
            return await handler(event, data)

        state: FSMContext = data.get("state")

        bot_user: BotUser | None = (
                await self._get_user_from_state(state, event, data)
                or await self._get_user_from_api(from_user, event, data)
        )

        if bot_user is None:
            return await handler(event, data)

        await self._update_user(bot_user, from_user)
        await self._update_bot_user(bot_user, state, event, chat)

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

    async def _get_user_from_state(
            self,
            state: FSMContext,
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> BotUser | None:
        try:
            user_id = UUID(await state.get_value("user_id"))

            bot_user: BotUser | None = await self._bot_users.get(
                user_id,
                event=event,
                workflow_data=data,
                from_json_method=BotUser.from_workflow_data
            )
        except (TypeError, ValueError):
            bot_user = None

        return bot_user

    async def _get_user_from_api(
            self,
            from_user: AiogramUser,
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> BotUser | None:
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
                return

        return BotUser.from_workflow_data(
            user.to_json(),
            controller=self._bot_users,
            event=event,
            workflow_data=data
        )

    async def _update_user(
            self,
            bot_user: BotUser,
            from_user: AiogramUser
    ) -> None:
        update_values: Dict[str, Any] = {}

        if bot_user.first_name != from_user.first_name:
            bot_user.first_name = from_user.first_name
            update_values["first_name"] = from_user.first_name

        if bot_user.username != from_user.username:
            bot_user.username = from_user.username
            update_values["username"] = from_user.username

        if update_values:
            await self._users.update_user(
                bot_user.id,
                **update_values
            )

    @staticmethod
    async def _update_bot_user(
            bot_user: BotUser,
            state: FSMContext,
            event: TelegramObject,
            chat: Chat | None = None
    ) -> None:
        if chat is not None:
            if bot_user.chat_id is None:
                bot_user.chat_id = chat.id

        if isinstance(event, CallbackQuery):
            if bot_user.message_id is None:
                bot_user.message_id = event.message.message_id

        await state.update_data(user_id=str(bot_user.id))
        await bot_user.save()
