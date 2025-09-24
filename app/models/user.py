from datetime import datetime
from uuid import UUID

from app.models.abstract import AbstractModel


class User(AbstractModel):
    id: UUID
    telegram_id: int
    first_name: str
    username: str
    locale: str | None
    created_at: datetime
    updated_at: datetime | None


class CreateUser(AbstractModel):
    telegram_id: int
    first_name: str
    username: str
    locale: str | None = None
