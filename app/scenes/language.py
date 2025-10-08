from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message

from app.actions.choose_language import ChooseLanguageAction
from app.models.bot_user import BotUser
from app.scenes.base import BaseScene
from app.utils.logging import logger


class LanguageScene(BaseScene, state="language"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await user.language_message()
        await callback_query.answer()

    @on.callback_query(ChooseLanguageAction.filter())
    async def on_choose_language(
            self,
            callback_query: CallbackQuery,
            callback_data: ChooseLanguageAction,
            user: BotUser
    ) -> None:
        await user.choose_language(new_language=callback_data.language_type)

        await self.wizard.back(
            user=user,
            locale=callback_data.language_type
        )
        await callback_query.answer()

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"set language to \'{callback_data.language_type}\'"
        )

    async def on_back(
            self,
            user: BotUser
    ) -> None:
        await self.wizard.back(user=user)

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
