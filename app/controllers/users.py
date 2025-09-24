from uuid import UUID

from app.controllers.abstract import APIController, AttributedDict
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import CreateUser, User


class UsersController(APIController):
    async def create_user(
            self,
            telegram_id: int,
            first_name: str,
            username: str,
            locale: str | None = None
    ) -> User:
        response: AttributedDict = await self._post(
            "users",
            json=CreateUser(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username,
                locale=locale
            ).model_dump()
        )

        if response.status_code == 409:
            raise AlreadyExistsError("User with provided username already exists")

        return User.from_dict(response)

    async def get_user(
            self,
            telegram_id: int
    ) -> User | None:
        response: AttributedDict = await self._get(
            f"users/telegram/{telegram_id}"
        )

        if response.status_code == 404:
            return

        return User.from_dict(response)

    async def get_user_locale(
            self,
            user_id: UUID
    ) -> str | None:
        response: AttributedDict = await self._get(
            f"users/locales/{user_id}"
        )

        if response.status_code == 404:
            return

        return response.locale

    async def update_user_locale(
            self,
            user_id: UUID,
            locale: str
    ) -> None:
        await self._put(
            f"users/locales/{user_id}",
            json={"locale": locale}
        )
