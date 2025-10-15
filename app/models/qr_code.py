from typing import Any, ClassVar
from uuid import UUID

from app.models.redis import AbstractRedisModel
from app.parameters import Parameters


class QRCode(AbstractRedisModel):
    """
    Represents a QR-Code in a Redis database.
    """

    key: ClassVar[str] = "qr_code"

    game_id: UUID | str
    file_id: str | None = None

    @property
    def primary_key(self) -> Any:
        """
        Primary key represented by a game UUID.
        :return: Game UUID.
        """

        return self.game_id


class BlurredQRCode(QRCode):
    """
    Represents a blurred QR-Code in a Redis database.
    """

    game_id: str = Parameters.DEFAULT_BLURRED_QR_CODE_KEY
