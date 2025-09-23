from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.controllers.users import UsersController
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import CreateUser, User

start_router = Router(name=__name__)


@start_router.message(CommandStart())
async def on_start_command(message: Message, users: UsersController) -> None:
    user: User = await users.get_user(message.from_user.id)

    if user is None:
        try:
            user = await users.create_user(
                CreateUser(
                    telegram_id=message.from_user.id,
                    first_name=message.from_user.first_name,
                    username=message.from_user.username,
                    locale=message.from_user.language_code
                )
            )
        except AlreadyExistsError:
            return

    await message.reply(
        _("message.start.main").format(
            first_name=user.first_name
        )
    )
