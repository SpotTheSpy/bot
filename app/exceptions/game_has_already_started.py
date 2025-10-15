from app.exceptions.api import APIError


class GameHasAlreadyStartedError(APIError):
    """
    Raised when user tries to perform an action which cannot be processed in a started game.
    """

    status_code: int = 400
