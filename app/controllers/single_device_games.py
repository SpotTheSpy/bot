from uuid import UUID

from app.assets.single_device_game import SingleDeviceGame
from app.controllers.abstract import APIController, AttributedDict
from app.exceptions.already_in_game import AlreadyInGameError
from app.models.single_device_game import CreateSingleDeviceGame


class SingleDeviceGamesController(APIController):
    async def create_game(
            self,
            user_id: UUID,
            telegram_id: int,
            secret_word: str,
            player_amount: int
    ) -> SingleDeviceGame:
        response: AttributedDict = await self._post(
            "single_device_games",
            json=CreateSingleDeviceGame(
                user_id=user_id,
                telegram_id=telegram_id,
                secret_word=secret_word,
                player_amount=player_amount
            ).model_dump()
        )

        if response.status_code == 400:
            raise AlreadyInGameError("You are already in game")

        return SingleDeviceGame.from_dict(response)

    async def get_game(
            self,
            game_id: UUID
    ) -> SingleDeviceGame | None:
        response: AttributedDict = await self._get(
            f"single_device_games/{game_id}"
        )

        if response.status_code == 404:
            return

        return SingleDeviceGame.from_dict(response)

    async def get_game_by_user_id(
            self,
            user_id: UUID
    ) -> SingleDeviceGame | None:
        response: AttributedDict = await self._get(
            f"single_device_games/by_user_id/{user_id}"
        )

        if response.status_code == 404:
            return

        return SingleDeviceGame.from_dict(response)

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        await self._delete(
            f"single_device_games/{game_id}"
        )
