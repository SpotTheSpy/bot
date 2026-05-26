from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from src.bot.actions.switch_language import SwitchLanguageAction
from src.bot.keyboards.language import language_keyboard
from src.bot.scenes.base import BaseScene
from src.core.enums.locale import Locale
from src.core.models.redis.user import User


class LanguageScene(BaseScene, state="language"):
    """
    Scene for switching the language.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        await user.message.edit(
            i18n.get("language"),
            reply_markup=language_keyboard(),
        )

        await callback_query.answer()

    @on.callback_query(SwitchLanguageAction.filter())
    async def on_switch_language(
            self,
            callback_query: CallbackQuery,
            callback_data: SwitchLanguageAction,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        previous_selected_locale: str | None = await state.get_value("selected_locale")

        if previous_selected_locale is not None:
            if callback_data.locale == Locale(previous_selected_locale):
                await callback_query.answer()
                return

        await user.message.edit(
            i18n.get(
                "language",
                callback_data.locale,
            ),
            reply_markup=language_keyboard(callback_data.locale),
        )

        await callback_query.answer()
        await state.update_data(selected_locale=callback_data.locale)

    @on.callback_query.leave()
    async def on_leave(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        selected_locale: str | None = await state.get_value("selected_locale")
        if selected_locale is None:
            return

        selected_locale: Locale = Locale(selected_locale)
        if selected_locale == user.locale:
            return

        await i18n.set_locale(selected_locale)
        await callback_query.answer(
            i18n.get(
                "language.answer-success",
                selected_locale,
            )
        )

        await state.update_data(selected_locale=None)

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
