from app.exceptions.api import APIError


class NotInGameError(APIError):
    """
    Raised when user tries to perform an action in a specific game while not being in it.
    """

    status_code: int = 409
