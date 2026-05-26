from enum import StrEnum, auto


class SpyCategory(StrEnum):
    """
    Category of secret words in the spy game.
    """

    GENERAL = auto()
    FOOD = auto()
    NATURE = auto()
    ANIMALS = auto()
    PLACES = auto()
    CELEBRITIES = auto()
