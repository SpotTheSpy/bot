from app.exceptions.api import APIError


class GameHasAlreadyStartedError(APIError):
    status_code: int = 400
