from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.actions.back import BackAction
from app.actions.choose_language import ChooseLanguageAction
from app.controllers.users import UsersController
from app.enums.language_type import LanguageType
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.models.user import User
from app.scenes.base import BaseScene


class LanguageScene(BaseScene, state="language"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.edit_message(
            callback_query.message,
            _("message.language.choose"),
            reply_markup=InlineKeyboardFactory.choose_language_keyboard()
        )

    @on.callback_query(ChooseLanguageAction.filter())
    async def on_choose_language(
            self,
            callback_query: CallbackQuery,
            callback_data: ChooseLanguageAction,
            state: FSMContext,
            user: User,
            users: UsersController
    ) -> None:
        locale: str | None = await state.get_value("locale")
        previous_language: LanguageType | None = LanguageType(locale) if locale else None

        if previous_language == callback_data.language_type:
            await callback_query.answer(_("answer.language.same"))
            return

        await users.update_user_locale(
            user.id,
            callback_data.language_type
        )

        await state.update_data(locale=callback_data.language_type)
        await self.wizard.back(locale=callback_data.language_type)

    @on.callback_query(BackAction.filter())
    async def on_back(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.wizard.back()

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
