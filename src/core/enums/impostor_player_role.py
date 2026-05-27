from enum import StrEnum, auto


class ImpostorPlayerRole(StrEnum):
    """
    Role of a player in the impostor game.
    """

    CITIZEN = auto()
    IMPOSTOR = auto()
