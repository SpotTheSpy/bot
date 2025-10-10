from app.exceptions.api import APIError


class AlreadyExistsError(APIError):
    status_code: int = 409
