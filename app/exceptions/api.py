from aiogram.exceptions import AiogramError


class APIError(AiogramError):
    status_code: int = 400
