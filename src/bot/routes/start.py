from aiogram import Router
from aiogram.filters import CommandStart

from src.bot.scenes.start import StartScene

start_router: Router = Router(name=__name__)

start_router.message.register(
    StartScene.as_handler(),
    CommandStart(deep_link=False),
)
