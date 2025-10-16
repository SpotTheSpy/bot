from app.exceptions.api import APIError


class NotFoundError(APIError):
    """
    Raised when an object is not found.
    """

    status_code: int = 404
