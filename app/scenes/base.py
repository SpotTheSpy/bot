from abc import ABC

from aiogram.fsm.scene import Scene, on
from aiogram.types import CallbackQuery

from app.actions.back import BackAction
from app.scenes.abstract import AbstractScene


class BaseScene(Scene, AbstractScene, ABC, state="base"):
    async def on_back(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.back()

    @on.callback_query(BackAction.filter())
    async def __on_back(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.on_back(callback_query)
