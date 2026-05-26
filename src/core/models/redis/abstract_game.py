from abc import ABC
from uuid import UUID

from src.core.models.redis.abstract import AbstractRedisModel


class AbstractGame(AbstractRedisModel, ABC):
    """
    Represents any active game.
    """

    id: UUID
    """
    Game ID.
    """

    host_id: UUID
    """
    ID of a user who hosts the game.
    """

    player_count: int
    """
    Count of players in game.
    """

    @property
    def primary_key(self) -> UUID:
        """
        Returns game ID.

        :return: Game ID.
        """

        return self.id
