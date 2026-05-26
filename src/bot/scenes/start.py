from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext

from src.bot.keyboards.greeting import greeting_keyboard
from src.bot.scenes.base import BaseScene
from src.core.models.redis.user import User


class StartScene(BaseScene, state="start", reset_history_on_enter=True):
    """
    Landing scene.
    """

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user: User,
            i18n: I18nContext,
    ) -> None:
        await user.message.replace(
            i18n.get(
                "greeting",
                first_name=message.from_user.first_name,
            ),
            reply_markup=greeting_keyboard(),
            message_to_delete=message.message_id,
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get(
                "greeting",
                first_name=callback_query.from_user.first_name,
            ),
            reply_markup=greeting_keyboard(),
        )

        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
