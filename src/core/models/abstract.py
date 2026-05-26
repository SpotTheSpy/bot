from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AbstractModel(BaseModel, ABC, arbitrary_types_allowed=True, from_attributes=True):
    """
    Abstract game model class. Used to define any domain object, such as game, user - anything.
    """

    @classmethod
    @abstractmethod
    def new(
            cls,
            *args: Any,
            **kwargs: Any,
    ) -> "AbstractModel":
        """
        Factory method for specific model class which should be used for new object creations.
        """
