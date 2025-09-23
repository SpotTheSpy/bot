from aiogram import F
from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.actions.play import PlayAction
from app.keyboards.inline_keyboard_factory import InlineKeyboardFactory
from app.controllers.users import UsersController
from app.enums.game_style import GameStyle
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import User
from app.scenes.base import BaseScene


class StartScene(BaseScene, state="start", reset_data_on_enter=True, reset_history_on_enter=True):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            users: UsersController
    ) -> None:
        user: User = await users.get_user(message.from_user.id)

        if user is None:
            try:
                user = await users.create_user(
                    message.from_user.id,
                    message.from_user.first_name,
                    message.from_user.username,
                    message.from_user.language_code
                )
            except AlreadyExistsError:
                return

        await message.delete()

        await message.answer(
            _("message.start.main").format(
                first_name=user.first_name
            ),
            reply_markup=InlineKeyboardFactory.start_keyboard()
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            users: UsersController
    ) -> None:
        user: User = await users.get_user(callback_query.from_user.id)

        if user is None:
            try:
                user = await users.create_user(
                    callback_query.from_user.id,
                    callback_query.from_user.first_name,
                    callback_query.from_user.username,
                    callback_query.from_user.language_code
                )
            except AlreadyExistsError:
                return

        await callback_query.message.edit_text(
            _("message.start.main").format(
                first_name=user.first_name
            ),
            reply_markup=InlineKeyboardFactory.start_keyboard()
        )

    @on.callback_query(PlayAction.filter(F.style == GameStyle.SINGLE_DEVICE))
    async def on_play_single_device(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.wizard.goto("explain_single_device")

    @on.callback_query(PlayAction.filter(F.style == GameStyle.MULTI_DEVICE))
    async def on_play_multi_device(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await callback_query.answer()
        await self.wizard.goto("explain_multi_device")

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()
