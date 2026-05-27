from typing import Tuple, Any
from uuid import UUID

from uuid_extensions import uuid7

from src.core.enums.imposter_count import ImposterCount
from src.core.models.redis.imposter_game.abstract import AbstractImposterGame


class SingleDeviceImposterGame(AbstractImposterGame):
    """
    Represents a single-device imposter game.
    """

    imposter_indices: Tuple[int, ...] | None = None
    """
    Indices of imposters in game.
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
        Set random imposter indices and empty answers after an object initialization.
        """

        if self.imposter_indices is None:
            self.imposter_indices = self.imposter_count.get_indices(self.player_count)

        if self.answers is None:
            self.answers = (None,) * self.player_count

    @classmethod
    def new(
            cls,
            host_id: UUID,
            player_count: int,
            real_question: str,
            imposter_question: str,
            imposter_count: ImposterCount,
            *,
            game_id: UUID | None = None,
    ) -> "SingleDeviceImposterGame":
        """
        Generate a new instance using only required parameters.

        :param host_id: Host ID.
        :param player_count: Count of players.
        :param real_question: Question which citizens get.
        :param imposter_question: Question which imposter(s) get.
        :param imposter_count: Count of imposters.
        :param game_id: Optional game ID, created if None.
        :return: New single-device imposter game instance.
        """

        return cls(
            id=game_id or uuid7(),
            host_id=host_id,
            player_count=player_count,
            real_question=real_question,
            imposter_question=imposter_question,
            imposter_count=imposter_count,
        )

    @classmethod
    def key(cls) -> str:
        return "single_device_imposter_game"
