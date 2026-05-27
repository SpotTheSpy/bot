from enum import StrEnum, auto


class ImposterPlayerRole(StrEnum):
    """
    Role of a player in the imposter game.
    """

    CITIZEN = auto()
    IMPOSTER = auto()
