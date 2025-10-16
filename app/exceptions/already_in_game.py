from app.exceptions.api import APIError


class AlreadyInGameError(APIError):
    """
    Raised when a user who tries to host or join a game is already in another game.
    """

    status_code: int = 409
