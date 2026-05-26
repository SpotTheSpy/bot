from abc import ABC

from src.core.enums.spy_category import SpyCategory
from src.core.enums.spy_count import SpyCount
from src.core.models.redis.abstract_game import AbstractGame


class AbstractSpyGame(AbstractGame, ABC):
    """
    Represent a spy game.
    """

    secret_word: str
    """
    Secret word tag.
    """

    category: SpyCategory
    """
    Secret word category.
    """

    spy_count: SpyCount
    """
    Count of spies.
    """
