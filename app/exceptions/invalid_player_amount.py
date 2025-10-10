from app.exceptions.api import APIError


class InvalidPlayerAmountError(APIError):
    status_code: int = 406
