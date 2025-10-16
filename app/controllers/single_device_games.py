from uuid import UUID

from app.controllers.api import APIController, AttributedDict
from app.exceptions.already_in_game import AlreadyInGameError
from app.exceptions.not_found import NotFoundError
from app.models.single_device_game import CreateSingleDeviceGame
from app.models.single_device_game import SingleDeviceGame


class SingleDeviceGamesController(APIController):
    """
    Single-device games API controller class.

    Provides methods for interacting with single-device games API endpoints.
    """

    async def create_game(
            self,
            user_id: UUID,
            player_amount: int
    ) -> SingleDeviceGame:
        """
        Create a new single-device game.

        :param user_id: Host UUID.
        :param player_amount: Count of players.

        :raise AlreadyInGameError: If you are already hosting a single-device game.
        :return: A created single-device game model.
        """

        response: AttributedDict = await self._post(
            "single_device_games",
            json=CreateSingleDeviceGame(
                user_id=user_id,
                player_amount=player_amount
            ).model_dump(mode="json")
        )

        if response.status_code == AlreadyInGameError.status_code:
            raise AlreadyInGameError("You are already in game")

        return SingleDeviceGame.from_json(response)

    async def get_game(
            self,
            game_id: UUID
    ) -> SingleDeviceGame | None:
        """
        Retrieve a single-device game by game UUID.

        Returns single-device game model if exists, otherwise None.
        """

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
        """
        Retrieve a single-device game by host UUID.

        Returns single-device game model if exists, otherwise None.
        """

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
        """
        Remove a single-device game by game UUID.
        """

        await self._delete(
            f"single_device_games/{game_id}"
        )

    async def restart_game(
            self,
            game_id: UUID
    ) -> SingleDeviceGame | None:
        """
        Restart a single-device game by game UUID.

        Returns single-device game model of a restarted game if was found, otherwise None.
        """

        response: AttributedDict = await self._post(
            f"single_device_games/{game_id}/restart"
        )

        if response.status_code == NotFoundError.status_code:
            return

        return SingleDeviceGame.from_json(response)
