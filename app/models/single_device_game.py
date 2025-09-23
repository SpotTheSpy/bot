from uuid import UUID

from pydantic import BaseModel


class CreateSingleDeviceGame(BaseModel):
    user_id: UUID
    telegram_id: int
    secret_word: str
    player_amount: int
