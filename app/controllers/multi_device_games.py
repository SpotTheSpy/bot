from uuid import UUID

from app.controllers.api import APIController, AttributedDict
from app.exceptions.already_in_game import AlreadyInGameError
from app.exceptions.game_has_already_started import GameHasAlreadyStartedError
from app.exceptions.invalid_player_amount import InvalidPlayerAmountError
from app.exceptions.not_found import NotFoundError
from app.exceptions.not_in_game import NotInGameError
from app.models.multi_device_game import CreateMultiDeviceGame
from app.models.multi_device_game import MultiDeviceGame


class MultiDeviceGamesController(APIController):
    """
    Multi-device games API controller class.

    Provides methods for interacting with multi-device games API endpoints.
    """

    async def create_game(
            self,
            host_id: UUID,
            player_amount: int
    ) -> MultiDeviceGame:
        """
        Create a new multi-device game.

        :param host_id: Host UUID.
        :param player_amount: Count of players.

        :raise AlreadyInGameError: If you are already in a multi-device game.
        :return: A created multi-device game model.
        """

        response: AttributedDict = await self._post(
            "multi_device_games",
            json=CreateMultiDeviceGame(
                host_id=host_id,
                player_amount=player_amount
            ).model_dump(mode="json")
        )

        if response.status_code == AlreadyInGameError.status_code:
            raise AlreadyInGameError("You are already in game")

        return MultiDeviceGame.from_json(response)

    async def get_game(
            self,
            game_id: UUID
    ) -> MultiDeviceGame | None:
        """
        Retrieve a multi-device game by game UUID.

        :param game_id: Game UUID.
        :return: A multi-device game model.
        """

        response: AttributedDict = await self._get(
            f"multi_device_games/{game_id}"
        )

        if response.status_code == NotFoundError.status_code:
            return

        return MultiDeviceGame.from_json(response)

    async def get_game_by_user_id(
            self,
            user_id: UUID
    ) -> MultiDeviceGame | None:
        """
       Retrieve a multi-device game by user UUID.

       :param user_id: User UUID.
       :return: A multi-device game model.
       """

        response: AttributedDict = await self._get(
            f"multi_device_games/by_user_id/{user_id}"
        )

        if response.status_code == NotFoundError.status_code:
            return

        return MultiDeviceGame.from_json(response)

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        """
        Remove a multi-device game by game UUID.

        :param game_id: Game UUID.
        """

        await self._delete(
            f"multi_device_games/{game_id}"
        )

    async def join_game(
            self,
            game_id: UUID,
            user_id: UUID
    ) -> MultiDeviceGame:
        """
        Join a multi-device game by game UUID.

        :param game_id: Game UUID.
        :param user_id: User UUID.
        :raise NotFoundError: If a game was not found.
        :raise GameHasAlreadyStartedError: If a game has already started.
        :raise AlreadyInGameError: If a user is already in another game.
        :raise InvalidPlayerAmountError: If a game has too many players.
        :return: A multi-device game model.
        """

        response: AttributedDict = await self._post(
            f"multi_device_games/{game_id}/join/{user_id}"
        )

        if response.status_code == NotFoundError.status_code:
            raise NotFoundError("Game with provided UUID was not found")
        if response.status_code == GameHasAlreadyStartedError.status_code:
            raise GameHasAlreadyStartedError("Game has already started")
        if response.status_code == AlreadyInGameError.status_code:
            raise AlreadyInGameError("You are already in game")
        if response.status_code == InvalidPlayerAmountError.status_code:
            raise InvalidPlayerAmountError("Game has too many players")

        return MultiDeviceGame.from_json(response)

    async def leave_game(
            self,
            user_id: UUID
    ) -> MultiDeviceGame | None:
        """
        Leave a multi-device game by game UUID.

        :param user_id: User UUID.
        :raise NotFoundError: If a user or game was not found.
        :raise NotInGameError: If a user is not in game.
        :return: A multi-device game model.
        """

        response: AttributedDict = await self._post(
            f"multi_device_games/leave/{user_id}"
        )

        if response.status_code == NotFoundError.status_code:
            raise NotFoundError("Game with provided UUID was not found")
        if response.status_code == NotInGameError.status_code:
            raise NotInGameError("You are not in game")

        return MultiDeviceGame.from_json(response)

    async def start_game(
            self,
            game_id: UUID
    ) -> MultiDeviceGame:
        """
        Start a multi-device game by game UUID

        :param game_id: Game UUID.
        :raise NotFoundError: If a game was not found.
        :raise GameHasAlreadyStartedError: If a game has already started.
        :raise InvalidPlayerAmountError: If a game has too few players.
        :return: A multi-device game model.
        """

        response: AttributedDict = await self._post(
            f"multi_device_games/{game_id}/start"
        )

        if response.status_code == NotFoundError.status_code:
            raise NotFoundError("Game with provided UUID was not found")
        if response.status_code == GameHasAlreadyStartedError.status_code:
            raise GameHasAlreadyStartedError("Game has already started")
        if response.status_code == InvalidPlayerAmountError.status_code:
            raise InvalidPlayerAmountError("Game has too few players")

        return MultiDeviceGame.from_json(response)

    async def restart_game(
            self,
            game_id: UUID
    ) -> MultiDeviceGame | None:
        """
        Restart a multi-device game by game UUID

        :param game_id: Game UUID.
        :return: A multi-device game model.
        """

        response: AttributedDict = await self._post(
            f"multi_device_games/{game_id}/restart"
        )

        if response.status_code == NotFoundError.status_code:
            return

        return MultiDeviceGame.from_json(response)

    async def generate_qr_code(
            self,
            game_id: UUID
    ) -> MultiDeviceGame | None:
        """
        Generate a QR-Code for multi-device game by game UUID

        :param game_id: Game UUID.
        :return: A multi-device game model.
        """

        response: AttributedDict = await self._post(
            f"multi_device_games/{game_id}/qr_code"
        )

        if response.status_code == NotFoundError.status_code:
            return

        return MultiDeviceGame.from_json(response)
