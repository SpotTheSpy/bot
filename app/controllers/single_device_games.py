from uuid import UUID

from app.controllers.abstract import APIController, AttributedDict
from app.exceptions.already_in_game import AlreadyInGameError
from app.exceptions.not_found import NotFoundError
from app.models.single_device_game import CreateSingleDeviceGame
from app.models.single_device_game import SingleDeviceGame


class SingleDeviceGamesController(APIController):
    async def create_game(
            self,
            user_id: UUID,
            telegram_id: int,
            player_amount: int
    ) -> SingleDeviceGame:
        response: AttributedDict = await self._post(
            "single_device_games",
            json=CreateSingleDeviceGame(
                user_id=user_id,
                telegram_id=telegram_id,
                player_amount=player_amount
            ).to_json()
        )

        if response.status_code == AlreadyInGameError.status_code:
            raise AlreadyInGameError("You are already in game")

        return SingleDeviceGame.from_json(response)

    async def get_game(
            self,
            game_id: UUID
    ) -> SingleDeviceGame | None:
        response: AttributedDict = await self._get(
            f"single_device_games/{game_id}"
        )

        if response.status_code == NotFoundError.status_code:
            return

        return SingleDeviceGame.from_json(response)

    async def get_game_by_user_id(
            self,
            user_id: UUID
    ) -> SingleDeviceGame | None:
        response: AttributedDict = await self._get(
            f"single_device_games/by_user_id/{user_id}"
        )

        if response.status_code == NotFoundError.status_code:
            return

        return SingleDeviceGame.from_json(response)

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        await self._delete(
            f"single_device_games/{game_id}"
        )
