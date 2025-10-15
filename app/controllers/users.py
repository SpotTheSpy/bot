from typing import Any
from uuid import UUID

from app.controllers.api import APIController, AttributedDict
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import CreateUser, User, UpdateUser


class UsersController(APIController):
    """
    Users API controller class.

    Provides methods for interacting with user API endpoints.
    """

    async def create_user(
            self,
            telegram_id: int,
            first_name: str,
            username: str | None = None,
            locale: str | None = None
    ) -> User:
        response: AttributedDict = await self._post(
            "users",
            json=CreateUser(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username,
                locale=locale
            ).model_dump(mode="json")
        )

        if response.status_code == 409:
            raise AlreadyExistsError("User with provided username already exists")

        return User.from_json(response)

    async def get_user(
            self,
            telegram_id: int
    ) -> User | None:
        response: AttributedDict = await self._get(
            f"users/telegram/{telegram_id}"
        )

        if response.status_code == 404:
            return

        return User.from_json(response)

    async def update_user(
            self,
            user_id: UUID,
            **values: Any
    ) -> None:
        await self._put(
            f"users/{user_id}",
            json=UpdateUser(**values).model_dump(mode="json", exclude_unset=True)
        )
