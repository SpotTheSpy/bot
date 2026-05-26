from random import choice
from typing import Any, List, Set
from uuid import UUID

from pydantic import Field

from config import config
from src.core.assets.secret_words import get_secret_words
from src.core.enums.spy_category import SpyCategory
from src.core.models.redis.abstract import AbstractRedisModel


class SecretWordQueue(AbstractRedisModel):
    """
    Represents a queue of previously encountered secret words for each user.
    """

    user_id: UUID
    """
    User UUID.
    """

    secret_words: List[str] = Field(default_factory=list)
    """
    List of last secret words.
    """

    guaranteed_unique_count: int = config.game_parameters.GUARANTEED_UNIQUE_WORD_COUNT
    """
    Count of guaranteed unique words.
    """

    @classmethod
    def new(
            cls,
            user_id: UUID,
    ) -> "SecretWordQueue":
        return cls(
            user_id=user_id,
        )

    @classmethod
    def key(cls) -> str:
        return "secret_words_queue"

    @property
    def primary_key(self) -> UUID:
        """
       Returns user's ID.

       :return: User's ID.
       """

        return self.user_id

    def get_unique_word(
            self,
            category: SpyCategory = SpyCategory.GENERAL
    ) -> str:
        """
        Retrieve a new random semi-unique word.
        Retrieves a word which has not been retrieved in last few attempts and saves new queue to Redis.

        :return: Secret word tag as a string.
        """

        possible_words: Set[str] = get_secret_words(category)
        available_words: Set[str] = possible_words - set(self.secret_words)

        if not available_words:
            available_words = possible_words

        word: str = choice(list(available_words))

        self.secret_words.append(word)
        if len(self.secret_words) > self.guaranteed_unique_count:
            self.secret_words.pop(0)

        return word
