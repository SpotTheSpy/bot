from aiogram.fsm.scene import on
from aiogram.types import Message
from aiogram_i18n import I18nContext

from src.bot.scenes.base import BaseScene
from src.core.models.redis.user import User


class StartScene(BaseScene, state="start", reset_history_on_enter=True):
    @on.message.enter()
    async def on_message(
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
            message_to_delete=message.message_id,
        )
