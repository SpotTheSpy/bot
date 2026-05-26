from enum import StrEnum, auto


class SpyPlayerRole(StrEnum):
    """
    Role of a player in the spy game.
    """

    CITIZEN = auto()
    SPY = auto()
