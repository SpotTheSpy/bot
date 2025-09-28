from typing import List, TYPE_CHECKING, Any, Optional, Dict
from uuid import UUID

from aiogram.fsm.context import FSMContext

from app.enums.player_role import PlayerRole
from app.models.abstract import AbstractModel

if TYPE_CHECKING:
    from app.controllers.multi_device_games import MultiDeviceGamesController
else:
    MultiDeviceGamesController = Any


class MultiDevicePlayer(AbstractModel):
    user_id: UUID
    telegram_id: int
    first_name: str
    role: PlayerRole | None = None


class MultiDeviceGame(AbstractModel):
    game_id: UUID
    host_id: UUID
    has_started: bool
    player_amount: int
    secret_word: str
    players: List[MultiDevicePlayer]

    @classmethod
    async def from_context(
            cls,
            user_id: UUID,
            state: FSMContext,
            multi_device_games: MultiDeviceGamesController
    ) -> Optional['MultiDeviceGame']:
        game_json: Dict[str, Any] = await state.get_value("game")

        if game_json is not None:
            return cls.from_json(game_json)

        return await multi_device_games.get_game_by_user_id(user_id)


class CreateMultiDeviceGame(AbstractModel):
    host_id: UUID
    player_amount: int
