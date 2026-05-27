from enum import StrEnum, auto


class ImposterGameParameter(StrEnum):
    """
    Game parameters for an imposter game.
    """

    PLAYER_COUNT = auto()
    IMPOSTER_COUNT = auto()
