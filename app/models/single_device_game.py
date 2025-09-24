from uuid import UUID

from app.models.abstract import AbstractModel


class SingleDeviceGame(AbstractModel):
    game_id: UUID
    user_id: UUID
    telegram_id: int
    secret_word: str
    player_amount: int
    spy_index: int


class CreateSingleDeviceGame(AbstractModel):
    user_id: UUID
    telegram_id: int
    player_amount: int
