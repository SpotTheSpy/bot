from abc import ABC

from src.core.enums.impostor_count import ImpostorCount
from src.core.models.redis.abstract_game import AbstractGame


class AbstractImpostorGame(AbstractGame, ABC):
    """
    Represent an impostor game.
    """

    real_question: str
    """
    Question which citizens get.
    """

    impostor_question: str
    """
    Question which impostor(s) get.
    """

    impostor_count: ImpostorCount
    """
    Count of impostors.
    """
