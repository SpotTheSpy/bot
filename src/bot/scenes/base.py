from abc import ABC

from aiogram.fsm.scene import Scene, on
from aiogram.types import CallbackQuery

from src.bot.actions.back import BackAction
from src.bot.actions.switch_scene import SwitchSceneAction


class BaseScene(Scene, ABC, state="base"):
    """
    Base class for all scenes. Provides basic behaviour for back and switch scene callback actions.
    """

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery,
    ) -> None:
        """
        Base method for returning to the previous scene.
        """

        if await self.wizard.state.get_state() != "start":
            await self.wizard.back()

        await callback_query.answer()

    @on.callback_query(SwitchSceneAction.filter())
    async def on_switch_scene(
            self,
            callback_query: CallbackQuery,
            callback_data: SwitchSceneAction,
    ) -> None:
        """
        Base method for proceeding to a new scene.
        """

        await self.wizard.goto(callback_data.scene)
        await callback_query.answer()
