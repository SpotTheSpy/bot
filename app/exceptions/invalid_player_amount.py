from app.exceptions.api import APIError


class InvalidPlayerAmountError(APIError):
    """
    Raised when user tries to perform an action which will result in an invalid player count in the game.

    Possible when user tries to join a full game, or start a game with less than minimal acceptable player count.
    """

    status_code: int = 406
