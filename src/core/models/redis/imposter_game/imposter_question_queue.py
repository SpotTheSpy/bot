from random import choice
from typing import List, Set, Tuple, Dict
from uuid import UUID

from pydantic import Field

from config import config
from src.core.assets.imposter_questions import get_imposter_questions
from src.core.enums.imposter_player_role import ImposterPlayerRole
from src.core.models.redis.abstract import AbstractRedisModel


class ImposterQuestionQueue(AbstractRedisModel):
    """
    Represents a queue of previously encountered imposter game questions for each user.
    """

    user_id: UUID
    """
    User UUID.
    """

    real_questions: List[str] = Field(default_factory=list)
    """
    List of last citizen questions.
    """

    imposter_questions: List[str] = Field(default_factory=list)
    """
    List of last imposter questions.
    """

    guaranteed_unique_count: int = config.game_parameters.GUARANTEED_UNIQUE_QUESTION_COUNT
    """
    Count of guaranteed unique questions.
    """

    @classmethod
    def new(
            cls,
            user_id: UUID,
    ) -> "ImposterQuestionQueue":
        return cls(
            user_id=user_id,
        )

    @classmethod
    def key(cls) -> str:
        return "imposter_question_queue"

    @property
    def primary_key(self) -> UUID:
        """
       Returns user's ID.

       :return: User's ID.
       """

        return self.user_id

    def get_unique_question_pair(self) -> Tuple[str, str]:
        """
        Retrieve a new random semi-unique pair of questions.
        Retrieves a pair of questions which has not been retrieved in last few attempts and saves new queue to Redis.

        :return: Tuple of 2 question tags as a string.
        """

        possible_questions: Dict[str, Dict[ImposterPlayerRole, Set[str]]] = get_imposter_questions()

        for bucket in possible_questions.values():
            bucket[ImposterPlayerRole.CITIZEN] -= set(self.real_questions)
            bucket[ImposterPlayerRole.IMPOSTER] -= set(self.imposter_questions)

        available_questions: Dict[str, Dict[ImposterPlayerRole, Set[str]]] = {
            bucket_key: bucket
            for bucket_key, bucket in possible_questions.items()
            if bucket[ImposterPlayerRole.CITIZEN] and bucket[ImposterPlayerRole.IMPOSTER]
        }

        bucket: Dict[ImposterPlayerRole, Set[str]] = choice(list(available_questions.values()))

        real_question: str = choice(list(bucket[ImposterPlayerRole.CITIZEN]))
        imposter_question: str = choice(list(bucket[ImposterPlayerRole.IMPOSTER]))

        self.real_questions.append(real_question)
        if len(self.real_questions) > self.guaranteed_unique_count:
            self.real_questions.pop(0)

        self.imposter_questions.append(imposter_question)
        if len(self.imposter_questions) > self.guaranteed_unique_count:
            self.imposter_questions.pop(0)

        return real_question, imposter_question
