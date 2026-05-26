from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from pydantic import ValidationError

from src.core.models.abstract import AbstractModel


class AbstractRedisModel(AbstractModel, ABC):
    """
    Base class for Redis models.

    This is an abstract class for objects which represent specific values in a Redis database.

    Redis key is usually constructed from a default redis key from a controller instance,
    a key class argument unique for every redis model class,
    and a primary key which must be unique for every redis object.

    Value is a JSON-Serialized object by to_json() method.
    """

    @classmethod
    @abstractmethod
    def key(cls) -> str:
        """
        Unique model class key.

        :return: Unique model class key.
        """

    @property
    @abstractmethod
    def primary_key(self) -> Any:
        """
        Main and unique key of any model, a value by which any model can be explicitly identified.

        :return: Primary key of any type, must be JSON-Serializable.
        """

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any] | None,
            **kwargs: Any
    ) -> Optional["AbstractRedisModel"]:
        """
        Reconstruct a model instance from a JSON-Serialized dictionary.

        :param data: Dictionary to reconstruct a model instance.
        :param kwargs: Any additional JSON-Serializable parameters.
        :return: A model instance if validated successfully, else None.
        """

        if data is None:
            return

        data.update(kwargs)

        try:
            return cls.model_validate(data)
        except ValidationError:
            pass

    def to_json(
            self,
            *,
            exclude_unset: bool = False
    ) -> Dict[str, Any] | None:
        """
        Serialize a model instance to a JSON-Serializable dictionary.

        :param exclude_unset: Whether to exclude unset attributes.

        :raise PydanticSerializationError: If serialization fails.
        :return: A JSON-Serializable dictionary.
        """
        try:
            return self.model_dump(mode="json", exclude_unset=exclude_unset)
        except ValidationError:
            pass
