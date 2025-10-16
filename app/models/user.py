from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models.abstract import AbstractModel


class User(AbstractModel):
    """
    Represents a basic user model.

    Attributes:
        id: UUID.
        telegram_id: User's telegram ID.
        first_name: First name from telegram.
        username: Username from telegram.
        locale: User's locale. Used to localize telegram responses.
        created_at: User's creation date.
        updated_at: User's last update date.
    """

    id: UUID
    """
    UUID.
    """

    telegram_id: int
    """
    User's telegram ID.
    """

    first_name: str
    """
    First name from telegram.
    """

    username: str | None
    """
    Username from telegram.
    """

    locale: str | None
    """
    User's locale. Used to localize telegram responses.
    """

    created_at: datetime
    """
    User's creation date.
    """

    updated_at: datetime | None
    """
    User's last update date.
    """

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

    Attributes:
        telegram_id: User's telegram ID.
        first_name: First name from telegram.
        username: Username from telegram.
        locale: User's locale. Used to localize telegram responses.
    """

    telegram_id: int
    """
    User's telegram ID.
    """

    first_name: str
    """
    First name from telegram.
    """

    username: str | None
    """
    Username from telegram.
    """

    locale: str | None
    """
    User's locale. Used to localize telegram responses.
    """


class UpdateUser(BaseModel):
    """
    Model for updating a user.

    Attributes:
        telegram_id: User's telegram ID.
        first_name: First name from telegram.
        username: Username from telegram.
        locale: User's locale. Used to localize telegram responses.
    """

    telegram_id: int | None = None
    """
    User's telegram ID.
    """

    first_name: str | None = None
    """
    First name from telegram.
    """

    username: str | None = None
    """
    Username from telegram.
    """

    locale: str | None = None
    """
    User's locale. Used to localize telegram responses.
    """
