from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from pydantic import BaseModel, ValidationError


class AbstractModel(BaseModel, ABC, arbitrary_types_allowed=True):
    @property
    @abstractmethod
    def primary_key(self) -> Any:
        pass

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any] | None,
            **kwargs: Any
    ) -> Optional['AbstractModel']:
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
        try:
            return self.model_dump(mode="json", exclude_unset=exclude_unset)
        except ValidationError:
            pass
