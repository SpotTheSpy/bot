from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message

from app.actions.choose_language import ChooseLanguageAction
from app.logging import logger
from app.models.bot_user import BotUser
from app.scenes.base import BaseScene


class LanguageScene(BaseScene, state="language"):
    """
    Scene for choosing a bot language.
    """

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
        locale: str | None = await user.choose_language(new_language=callback_data.locale)

        await self.wizard.back(
            user=user,
            new_locale=locale
        )
        await callback_query.answer()

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"set language to \'{locale}\'"
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
