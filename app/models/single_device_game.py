from uuid import UUID

from pydantic import BaseModel

from app.models.abstract import AbstractModel


class SingleDeviceGame(AbstractModel):
    """
    Represents a single-device game.

    Attributes:
        game_id: UUID.
        user_id: Host UUID.
        player_amount: Count of players.
        secret_word: Game's secret word tag.
        spy_index: Index of a game's spy (From 0 to player amount).
    """

    game_id: UUID
    """
    UUID.
    """

    user_id: UUID
    """
    Host UUID.
    """

    secret_word: str
    """
    Game's secret word tag.
    """

    player_amount: int
    """
    Count of players.
    """

    spy_index: int
    """
    Index of a game's spy (From 0 to player amount).
    """

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

    Attributes:
        user_id: Host UUID.
        player_amount: Count of players.
    """

    user_id: UUID
    """
    Host UUID.
    """

    player_amount: int
    """
    Count of players.
    """
