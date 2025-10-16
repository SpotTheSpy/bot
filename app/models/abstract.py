from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from pydantic import BaseModel, ValidationError


class AbstractModel(BaseModel, ABC, arbitrary_types_allowed=True):
    """
    Abstract game model class.

    Used to define any model which is a part of the game,
    such as a game itself, QR-Code, or any other entity.
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
    ) -> Optional['AbstractModel']:
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
