from enum import StrEnum, auto


class ImpostorGameParameter(StrEnum):
    """
    Game parameters for an impostor game.
    """

    PLAYER_COUNT = auto()
    IMPOSTOR_COUNT = auto()
