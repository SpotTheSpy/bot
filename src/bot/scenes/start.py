from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext

from src.bot.keyboards.greeting import greeting_keyboard
from src.bot.logger import logger
from src.bot.scenes.base import BaseScene
from src.core.controllers.redis import RedisController
from src.core.enums.time_stamp import TimeStamp
from src.core.models.redis.impostor_game.single_device import SingleDeviceImpostorGame
from src.core.models.redis.spy_game.single_device import SingleDeviceSpyGame
from src.core.models.redis.user import User, ActiveGames


class StartScene(BaseScene, state="start", reset_data_on_enter=True, reset_history_on_enter=True):
    """
    Landing scene.
    """

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user: User,
            i18n: I18nContext,
            user_controller: RedisController[User],
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
            single_device_impostor_game_controller: RedisController[SingleDeviceImpostorGame],
    ) -> None:
        await user.message.replace(
            i18n.get("greeting"),
            reply_markup=greeting_keyboard(),
            message_to_delete=message.message_id,
        )

        await self._cleanup_games(
            user,
            user_controller,
            single_device_spy_game_controller,
            single_device_impostor_game_controller,
        )

        logger.info(
            f"{user.telegram_id} ({user.first_name}) opened the landing page."
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            i18n: I18nContext,
            user_controller: RedisController[User],
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
            single_device_impostor_game_controller: RedisController[SingleDeviceImpostorGame],
    ) -> None:
        await user.message.edit(
            i18n.get("greeting"),
            reply_markup=greeting_keyboard(),
        )

        await callback_query.answer()

        await self._cleanup_games(
            user,
            user_controller,
            single_device_spy_game_controller,
            single_device_impostor_game_controller,
        )

    @on.message()
    async def on_message(
            self,
            message: Message
    ) -> None:
        await message.delete()

    @staticmethod
    async def _cleanup_games(
            user: User,
            user_controller: RedisController[User],
            single_device_spy_game_controller: RedisController[SingleDeviceSpyGame],
            single_device_impostor_game_controller: RedisController[SingleDeviceImpostorGame],
    ) -> None:
        if user.active_games.active_single_device_spy_game is not None:
            await single_device_spy_game_controller.remove(user.active_games.active_single_device_spy_game)

        if user.active_games.active_single_device_impostor_game is not None:
            await single_device_impostor_game_controller.remove(user.active_games.active_single_device_impostor_game)

        user.active_games = ActiveGames.new()
        await user_controller.set(user, expire=TimeStamp.DAY)
