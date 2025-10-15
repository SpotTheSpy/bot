from aiogram.exceptions import AiogramError


class APIError(AiogramError):
    """
    Raised when a business-logic error is encountered.
    """

    status_code: int = 400
