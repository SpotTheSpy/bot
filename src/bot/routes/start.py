from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_i18n import I18nContext

from src.core.models.redis.user import User

start_router: Router = Router(name=__name__)


@start_router.message(CommandStart())
async def on_start(message: Message, user: User, i18n: I18nContext) -> None:
    print(user)
    await message.reply(i18n.get("example"))
