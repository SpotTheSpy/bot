from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models.abstract import AbstractModel


class User(AbstractModel):
    """
    Represents a basic user model.
    """

    id: UUID
    telegram_id: int
    first_name: str
    username: str | None
    locale: str | None
    created_at: datetime
    updated_at: datetime | None

    @property
    def primary_key(self) -> Any:
        """
        Primary key represented by a user UUID.
        :return: User UUID.
        """

        return self.id


class CreateUser(BaseModel):
    """
    Model for creating a user.
    """

    telegram_id: int
    first_name: str
    username: str | None
    locale: str | None = None


class UpdateUser(BaseModel):
    """
    Model for updating a user.
    """

    telegram_id: int | None = None
    first_name: str | None = None
    username: str | None = None
    locale: str | None = None
