from enum import StrEnum, auto
from random import shuffle, choices
from typing import Tuple, List


class ImpostorCount(StrEnum):
    """
    Count of impostors in the impostor game.
    """

    SINGLE = auto()
    DOUBLE = auto()
    RANDOM = auto()

    def get_indices(
            self,
            player_count: int,
    ) -> Tuple[int, ...]:
        """
        Retrieve random indices of impostors in game from player count.

        If impostor count is random, there is a 40% chance of either having one or two impostors,
        a 7.5% chance of having 0 impostors and a 2.5% chance of all players being impostors.

        :param player_count: Count of players.
        :return: Tuple of player indices.
        """

        indices: List[int] = list(range(player_count))
        shuffle(indices)

        match self:
            case self.SINGLE:
                selected_indices: List = indices[:1]
            case self.DOUBLE:
                selected_indices: List = indices[:2]
            case self.RANDOM:
                count: int = choices(
                    population=(1, 2, 0, len(indices)),
                    weights=(60, 30, 7.5, 2.5),
                )[0]
                selected_indices: List = indices[:count]
            case _:
                selected_indices: List = []

        return tuple(sorted(selected_indices))
