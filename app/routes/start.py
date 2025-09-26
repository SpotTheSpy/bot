from aiogram import Router
from aiogram.filters import CommandStart

from app.scenes.multi_device_play import MultiDevicePlayScene
from app.scenes.start import StartScene

start_router = Router(name=__name__)

start_router.message.register(
    MultiDevicePlayScene.as_handler(),
    CommandStart(deep_link=True, deep_link_encoded=True)
)

start_router.message.register(
    StartScene.as_handler(),
    CommandStart()
)
