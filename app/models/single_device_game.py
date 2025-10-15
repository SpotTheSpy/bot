from uuid import UUID

from pydantic import BaseModel

from app.models.abstract import AbstractModel


class SingleDeviceGame(AbstractModel):
    """
    Represents a single-device game.
    """

    game_id: UUID
    user_id: UUID
    secret_word: str
    player_amount: int
    spy_index: int

    @property
    def primary_key(self) -> UUID:
        """
        Primary key represented by a game UUID.
        :return: Game UUID.
        """

        return self.game_id


class CreateSingleDeviceGame(BaseModel):
    """
    Model for creating a single-device game.
    """

    user_id: UUID
    telegram_id: int
    player_amount: int
