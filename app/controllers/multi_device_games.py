from uuid import UUID

from app.controllers.abstract import APIController, AttributedDict
from app.exceptions.already_in_game import AlreadyInGameError
from app.exceptions.game_has_already_started import GameHasAlreadyStartedError
from app.exceptions.invalid_player_amount import InvalidPlayerAmountError
from app.exceptions.not_found import NotFoundError
from app.models.multi_device_game import CreateMultiDeviceGame, SetGameURLModel
from app.models.multi_device_game import MultiDeviceGame


class MultiDeviceGamesController(APIController):
    async def create_game(
            self,
            host_id: UUID,
            player_amount: int
    ) -> MultiDeviceGame:
        response: AttributedDict = await self._post(
            "multi_device_games",
            json=CreateMultiDeviceGame(
                host_id=host_id,
                player_amount=player_amount
            ).to_json()
        )

        if response.status_code == AlreadyInGameError.status_code:
            raise AlreadyInGameError("You are already in game")

        return MultiDeviceGame.from_json(response)

    async def get_game(
            self,
            game_id: UUID
    ) -> MultiDeviceGame | None:
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
        await self._delete(
            f"multi_device_games/{game_id}"
        )

    async def remove_game_by_user_id(
            self,
            user_id: UUID
    ) -> None:
        response: AttributedDict = await self._get(
            f"multi_device_games/by_user_id/{user_id}"
        )

        if response.status_code == NotFoundError.status_code:
            return

        game = MultiDeviceGame.from_json(response)

        await self._delete(
            f"multi_device_games/{game.game_id}"
        )

    async def join_game(
            self,
            game_id: UUID,
            user_id: UUID
    ) -> MultiDeviceGame:
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
            game_id: UUID,
            user_id: UUID
    ) -> None:
        await self._post(
            f"multi_device_games/{game_id}/leave/{user_id}"
        )

    async def start_game(
            self,
            game_id: UUID
    ) -> MultiDeviceGame:
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

    async def set_game_url(
            self,
            game_id: UUID,
            url: str
    ) -> MultiDeviceGame | None:
        response: AttributedDict = await self._post(
            f"multi_device_games/{game_id}/url",
            json=SetGameURLModel(url=url).to_json()
        )

        if response.status_code == NotFoundError.status_code:
            return

        return MultiDeviceGame.from_json(response)
