from abc import ABC

from src.core.enums.imposter_count import ImposterCount
from src.core.models.redis.abstract_game import AbstractGame


class AbstractImposterGame(AbstractGame, ABC):
    """
    Represent an imposter game.
    """

    real_question: str
    """
    Question which citizens get.
    """

    imposter_question: str
    """
    Question which imposter(s) get.
    """

    imposter_count: ImposterCount
    """
    Count of imposters.
    """
