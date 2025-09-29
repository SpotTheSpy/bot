from app.exceptions.api import APIError


class NotFoundError(APIError):
    status_code: int = 404
