from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.controllers.single_device_games import SingleDeviceGamesController
from app.exceptions.already_in_game import AlreadyInGameError
from app.models.single_device_game import SingleDeviceGame
from app.models.user import User
from app.scenes.base import BaseScene


class PlaySingleDeviceScene(BaseScene, state="play_single_device"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            state: FSMContext,
            single_games: SingleDeviceGamesController
    ) -> None:
        try:
            game: SingleDeviceGame = await single_games.create_game(
                user.id,
                user.telegram_id,
                "Apple",
                4
            )
        except AlreadyInGameError:
            await callback_query.answer(_("answer.play.already_in_game"))
            await self.wizard.back()
            return

        await state.update_data(game.to_json())

        await callback_query.message.edit_text(
            f"{game.to_json()}"
        )
