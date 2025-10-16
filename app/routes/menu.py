from aiogram import Router

from app.actions.menu import MenuAction
from app.scenes.start import StartScene

menu_router = Router(name=__name__)

# Handler for menu buttons.
menu_router.callback_query.register(
    StartScene.as_handler(),
    MenuAction.filter()
)
