from abc import ABC
from typing import Dict, Any

from pydantic import BaseModel


class AbstractModel(BaseModel, ABC):
    @classmethod
    def from_json(
            cls,
            json: Dict[str, Any]
    ) -> 'AbstractModel':
        return cls.model_validate(json)

    def to_json(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")
