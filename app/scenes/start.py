from aiogram.fsm.scene import on
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.controllers.users import UsersController
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import User
from app.scenes.base import BaseScene


class StartScene(BaseScene, state="start", reset_data_on_enter=True, reset_history_on_enter=True):
    @on.message.enter()
    async def on_enter(
            self,
            message: Message,
            users: UsersController
    ) -> None:
        user: User = await users.get_user(message.from_user.id)

        if user is None:
            try:
                user = await users.create_user(
                    message.from_user.id,
                    message.from_user.first_name,
                    message.from_user.username,
                    message.from_user.language_code
                )
            except AlreadyExistsError:
                return

        await message.delete()
        await message.answer(
            _("message.start.main").format(
                first_name=user.first_name
            )
        )

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
