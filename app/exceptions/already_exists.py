from app.exceptions.api import APIError


class AlreadyExistsError(APIError):
    """
    Raised when object with the same provided unique parameters already exists.
    """

    status_code: int = 409
