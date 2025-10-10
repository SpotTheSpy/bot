from app.exceptions.api import APIError


class NotInGameError(APIError):
    status_code: int = 409
