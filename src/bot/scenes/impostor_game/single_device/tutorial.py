from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from src.bot.keyboards.tutorial import tutorial_keyboard
from src.bot.scenes.base import BaseScene
from src.core.models.redis.user import User


class SingleDeviceImpostorGameTutorialScene(BaseScene, state="single_device_impostor_game_tutorial"):
    """
    Scene for the single device impostor game tutorial.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("tutorial-single-device-impostor-game"),
            reply_markup=tutorial_keyboard("single_device_impostor_game_setup"),
        )

        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
