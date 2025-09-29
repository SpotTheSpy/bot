from abc import ABC
from typing import Dict, Any, Optional

from pydantic import BaseModel, ValidationError


class AbstractModel(BaseModel, ABC):
    @classmethod
    def from_json(
            cls,
            json: Dict[str, Any]
    ) -> Optional['AbstractModel']:
        try:
            return cls.model_validate(json)
        except ValidationError:
            pass

    def to_json(self) -> Dict[str, Any] | None:
        try:
            return self.model_dump(mode="json")
        except ValidationError:
            pass
