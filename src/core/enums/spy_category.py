from enum import StrEnum, auto


class SpyCategory(StrEnum):
    """
    Category of secret words in the spy game.
    """

    GENERAL = auto()
    FOOD = auto()
    PLANTS = auto()
    ANIMALS = auto()
    PLACES = auto()
    GEOGRAPHY = auto()
    HOUSEHOLDS = auto()
    PROFESSIONS = auto()
    SPORTS = auto()
    MYTHOLOGY = auto()
    CELEBRITIES = auto()
    CHARACTERS = auto()
