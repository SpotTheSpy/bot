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
        """
        Create a new user.

        :param telegram_id: User's telegram ID.
        :param first_name: First name from telegram.
        :param username: Username from telegram.
        :param locale:  User's locale. Used to localize telegram responses.

        :raise AlreadyExistsError: If a user with the same telegram ID or username already exists.
        :return: A created user model.
        """

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
        """
        Retrieve a user by user ID.

        Returns user model if exists, otherwise None.
        """

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
        """
        Update a user by user ID.
        """

        await self._put(
            f"users/{user_id}",
            json=UpdateUser(**values).model_dump(mode="json", exclude_unset=True)
        )
