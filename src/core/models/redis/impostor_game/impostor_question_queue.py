from random import choice
from typing import List, Set, Tuple, Dict
from uuid import UUID

from pydantic import Field

from config import config
from src.core.assets.impostor_questions import get_impostor_questions
from src.core.enums.impostor_player_role import ImpostorPlayerRole
from src.core.models.redis.abstract import AbstractRedisModel


class ImpostorQuestionQueue(AbstractRedisModel):
    """
    Represents a queue of previously encountered impostor game questions for each user.
    """

    user_id: UUID
    """
    User UUID.
    """

    real_questions: List[str] = Field(default_factory=list)
    """
    List of last citizen questions.
    """

    impostor_questions: List[str] = Field(default_factory=list)
    """
    List of last impostor questions.
    """

    guaranteed_unique_count: int = config.game_parameters.GUARANTEED_UNIQUE_QUESTION_COUNT
    """
    Count of guaranteed unique questions.
    """

    @classmethod
    def new(
            cls,
            user_id: UUID,
    ) -> "ImpostorQuestionQueue":
        return cls(
            user_id=user_id,
        )

    @classmethod
    def key(cls) -> str:
        return "impostor_question_queue"

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

        possible_questions: Dict[str, Dict[ImpostorPlayerRole, Set[str]]] = get_impostor_questions()

        for bucket in possible_questions.values():
            bucket[ImpostorPlayerRole.CITIZEN] -= set(self.real_questions)
            bucket[ImpostorPlayerRole.IMPOSTOR] -= set(self.impostor_questions)

        available_questions: Dict[str, Dict[ImpostorPlayerRole, Set[str]]] = {
            bucket_key: bucket
            for bucket_key, bucket in possible_questions.items()
            if bucket[ImpostorPlayerRole.CITIZEN] and bucket[ImpostorPlayerRole.IMPOSTOR]
        }

        bucket: Dict[ImpostorPlayerRole, Set[str]] = choice(list(available_questions.values()))

        real_question: str = choice(list(bucket[ImpostorPlayerRole.CITIZEN]))
        impostor_question: str = choice(list(bucket[ImpostorPlayerRole.IMPOSTOR]))

        self.real_questions.append(real_question)
        if len(self.real_questions) > self.guaranteed_unique_count:
            self.real_questions.pop(0)

        self.impostor_questions.append(impostor_question)
        if len(self.impostor_questions) > self.guaranteed_unique_count:
            self.impostor_questions.pop(0)

        return real_question, impostor_question
