from app.exceptions.api import APIError


class AlreadyInGameError(APIError):
    status_code: int = 409
