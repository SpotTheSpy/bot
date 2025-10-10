from typing import Any, ClassVar
from uuid import UUID

from app.models.redis import AbstractRedisModel
from app.parameters import Parameters


class QRCode(AbstractRedisModel):
    key: ClassVar[str] = "qr_code"

    game_id: UUID | str
    file_id: str | None = None

    @property
    def primary_key(self) -> Any:
        return self.game_id


class BlurredQRCode(QRCode):
    game_id: str = Parameters.DEFAULT_BLURRED_QR_CODE_KEY
