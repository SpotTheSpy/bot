from typing import Tuple, Any
from uuid import UUID

from uuid_extensions import uuid7

from src.core.enums.spy_category import SpyCategory
from src.core.enums.spy_count import SpyCount
from src.core.models.redis.spy_game.abstract import AbstractSpyGame


class SingleDeviceSpyGame(AbstractSpyGame):
    """
    Represents a single-device spy game.
    """

    spy_indices: Tuple[int, ...] | None = None
    """
    Indices of spies in game.
    """

    def model_post_init(
            self,
            context: Any,
    ) -> None:
        """
        Set random spy indices after an object initialization.
        """

        if self.spy_indices is None:
            self.spy_indices = self.spy_count.get_indices(self.player_count)

    @classmethod
    def new(
            cls,
            host_id: UUID,
            player_count: int,
            secret_word: str,
            category: SpyCategory,
            spy_count: SpyCount,
            *,
            game_id: UUID | None = None,
    ) -> "SingleDeviceSpyGame":
        """
        Generate a new instance using only required parameters.

        :param host_id: Host ID.
        :param player_count: Count of players.
        :param secret_word: Game's secret word tag.
        :param category: Secret word category.
        :param spy_count: Count of spies.
        :param game_id: Optional game ID, created if None.
        :return: New single-device spy game instance.
        """

        return cls(
            id=game_id or uuid7(),
            host_id=host_id,
            player_count=player_count,
            secret_word=secret_word,
            category=category,
            spy_count=spy_count,
        )

    @classmethod
    def key(cls) -> str:
        return "single_device_spy_game"
