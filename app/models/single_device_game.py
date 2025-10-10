from uuid import UUID

from pydantic import BaseModel

from app.models.abstract import AbstractModel


class SingleDeviceGame(AbstractModel):
    game_id: UUID
    user_id: UUID
    secret_word: str
    player_amount: int
    spy_index: int

    @property
    def primary_key(self) -> UUID:
        return self.game_id


class CreateSingleDeviceGame(BaseModel):
    user_id: UUID
    telegram_id: int
    player_amount: int
