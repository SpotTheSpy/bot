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

    def to_json(
            self,
            *,
            exclude_unset: bool = False
    ) -> Dict[str, Any] | None:
        try:
            return self.model_dump(mode="json", exclude_unset=exclude_unset)
        except ValidationError:
            pass
