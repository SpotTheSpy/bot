from typing import Tuple, Any
from uuid import UUID

from uuid_extensions import uuid7

from src.core.enums.impostor_count import ImpostorCount
from src.core.models.redis.impostor_game.abstract import AbstractImpostorGame


class SingleDeviceImpostorGame(AbstractImpostorGame):
    """
    Represents a single-device impostor game.
    """

    impostor_indices: Tuple[int, ...] | None = None
    """
    Indices of impostors in game.
    """

    answers: Tuple[str | None, ...] | None = None
    """
    Sequence of answers collected from all the players.
    """

    def model_post_init(
            self,
            context: Any,
    ) -> None:
        """
        Set random impostor indices and empty answers after an object initialization.
        """

        if self.impostor_indices is None:
            self.impostor_indices = self.impostor_count.get_indices(self.player_count)

        if self.answers is None:
            self.answers = (None,) * self.player_count

    @classmethod
    def new(
            cls,
            host_id: UUID,
            player_count: int,
            real_question: str,
            impostor_question: str,
            impostor_count: ImpostorCount,
            *,
            game_id: UUID | None = None,
    ) -> "SingleDeviceImpostorGame":
        """
        Generate a new instance using only required parameters.

        :param host_id: Host ID.
        :param player_count: Count of players.
        :param real_question: Question which citizens get.
        :param impostor_question: Question which impostor(s) get.
        :param impostor_count: Count of impostors.
        :param game_id: Optional game ID, created if None.
        :return: New single-device impostor game instance.
        """

        return cls(
            id=game_id or uuid7(),
            host_id=host_id,
            player_count=player_count,
            real_question=real_question,
            impostor_question=impostor_question,
            impostor_count=impostor_count,
        )

    @classmethod
    def key(cls) -> str:
        return "single_device_impostor_game"
