from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    telegram_id: int
    first_name: str
    username: str
    locale: str | None
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_dict(
            cls,
            data: Dict[str, Any]
    ) -> 'User':
        return cls.model_validate(data)


class CreateUser(BaseModel):
    telegram_id: int
    first_name: str
    username: str
    locale: str | None = None
