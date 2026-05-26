from enum import StrEnum, auto


class SpyGameParameter(StrEnum):
    """
    Game parameters for a spy game.
    """

    PLAYER_COUNT = auto()
    CATEGORY = auto()
    SPY_COUNT = auto()
