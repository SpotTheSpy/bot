from typing import List
from uuid import UUID

from app.enums.player_role import PlayerRole
from app.models.abstract import AbstractModel


class MultiDevicePlayer(AbstractModel):
    user_id: UUID
    first_name: str
    role: PlayerRole | None = None


class CreateMultiDevicePlayer(AbstractModel):
    user_id: UUID
    first_name: str


class MultiDeviceGame(AbstractModel):
    game_id: UUID
    host_id: UUID
    has_started: bool
    player_amount: int
    secret_word: str
    players: List[MultiDevicePlayer]


class CreateMultiDeviceGame(AbstractModel):
    host_id: UUID
    player_amount: int
