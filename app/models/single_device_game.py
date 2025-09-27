from typing import Any, TYPE_CHECKING, Dict, Optional
from uuid import UUID

from aiogram.fsm.context import FSMContext

from app.models.abstract import AbstractModel

if TYPE_CHECKING:
    from app.controllers.single_device_games import SingleDeviceGamesController
else:
    SingleDeviceGamesController = Any


class SingleDeviceGame(AbstractModel):
    game_id: UUID
    user_id: UUID
    telegram_id: int
    secret_word: str
    player_amount: int
    spy_index: int

    @classmethod
    async def from_context(
            cls,
            user_id: UUID,
            state: FSMContext,
            single_device_games: SingleDeviceGamesController
    ) -> Optional['SingleDeviceGame']:
        game_json: Dict[str, Any] = await state.get_value("game")

        if game_json is not None:
            return SingleDeviceGame.from_json(game_json)

        return await single_device_games.get_game_by_user_id(user_id)


class CreateSingleDeviceGame(AbstractModel):
    user_id: UUID
    telegram_id: int
    player_amount: int
