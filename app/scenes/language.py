from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.choose_language import ChooseLanguageAction
from app.controllers.api.users import UsersController
from app.enums.language_type import LanguageType
from app.models.user import BotUser
from app.scenes.base import BaseScene
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.utils.logging import logger


class LanguageScene(BaseScene, state="language"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await callback_query.answer()
        await user.edit_message(
            text=_("message.language.choose"),
            reply_markup=InlineKeyboardFactory.choose_language_keyboard()
        )

    @on.callback_query(ChooseLanguageAction.filter())
    async def on_choose_language(
            self,
            callback_query: CallbackQuery,
            callback_data: ChooseLanguageAction,
            user: BotUser,
            users: UsersController
    ) -> None:
        locale: str | None = user.locale
        previous_language: LanguageType | None = LanguageType(locale) if locale else None

        if previous_language == callback_data.language_type:
            await callback_query.answer(_("answer.language.same"))
            return

        await users.update_user_locale(
            user.id,
            callback_data.language_type
        )

        user.locale = callback_data.language_type
        await user.save()

        await callback_query.answer()
        await self.wizard.back(
            user=user,
            locale=callback_data.language_type
        )

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"set language to \'{callback_data.language_type}\'"
        )

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery,
            user: BotUser
    ) -> None:
        await self.wizard.back(user=user)

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
