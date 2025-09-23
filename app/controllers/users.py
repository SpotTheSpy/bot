from app.controllers.abstract import APIController, AttributedDict
from app.exceptions.already_exists import AlreadyExistsError
from app.models.user import CreateUser, User


class UsersController(APIController):
    async def create_user(
            self,
            user: CreateUser
    ) -> User:
        response: AttributedDict = await self._post(
            "users",
            json=user.model_dump(exclude_unset=True)
        )

        if response.status_code == 409:
            raise AlreadyExistsError("User with provided username already exists")

        return User.from_dict(response)

    async def get_user(
            self,
            telegram_id: int
    ) -> User | None:
        response: AttributedDict = await self._get(
            f"users/{telegram_id}"
        )

        if response.status_code == 404:
            return

        return User.from_dict(response)

    async def get_user_locale(
            self,
            telegram_id: int
    ) -> str | None:
        response: AttributedDict = await self._get(
            f"users/locales/{telegram_id}"
        )

        if response.status_code == 404:
            return

        return response.locale

    async def update_user_locale(
            self,
            telegram_id: int,
            locale: str
    ) -> None:
        await self._put(
            f"users/locales/{telegram_id}",
            json={"locale": locale}
        )
