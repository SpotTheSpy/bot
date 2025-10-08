from base64 import urlsafe_b64encode
from typing import List, ClassVar
from uuid import UUID

from aiogram.types import InputFile, BufferedInputFile
from aiohttp import ClientSession
from pydantic import BaseModel

from app.controllers.redis import RedisController
from app.enums.payload_type import PayloadType
from app.enums.player_role import PlayerRole
from app.models.abstract import AbstractModel
from app.models.qr_code import QRCode
from app.parameters import Parameters

with open("app/data/blurred_qr_code.jpg", "rb") as __file:
    _BLURRED_QR_CODE_DATA: bytes = __file.read()


class MultiDevicePlayer(AbstractModel):
    user_id: UUID
    telegram_id: int
    first_name: str
    role: PlayerRole | None = None

    @property
    def primary_key(self) -> UUID:
        return self.user_id


class MultiDeviceGame(AbstractModel):
    __BLURRED_QR_CODE_DATA: ClassVar[bytes] = _BLURRED_QR_CODE_DATA

    game_id: UUID
    host_id: UUID
    has_started: bool
    player_amount: int
    secret_word: str
    qr_code_url: str | None
    players: List[MultiDevicePlayer]

    @property
    def primary_key(self) -> UUID:
        return self.game_id

    @property
    def join_url(self) -> str:
        payload: str = f"{PayloadType.JOIN}:{self.game_id}"
        encoded_payload: str = urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8").replace("=", "")
        return Parameters.TELEGRAM_BOT_START_URL.format(payload=encoded_payload)

    async def get_qr_code(
            self,
            qr_codes: RedisController[QRCode]
    ) -> InputFile | str | None:
        if self.qr_code_url is None:
            qr_code: QRCode = await qr_codes.get(Parameters.DEFAULT_BLURRED_QR_CODE_KEY)

            if qr_code is None or qr_code.file_id is None:
                return BufferedInputFile(self.__BLURRED_QR_CODE_DATA, "blurred.jpg")

            return qr_code.file_id

        qr_code: QRCode = await qr_codes.get(self.game_id)

        if qr_code is None or qr_code.file_id is None:
            async with ClientSession() as session:
                async with session.get(self.qr_code_url) as response:
                    if response.status != 200:
                        return

                    return BufferedInputFile(await response.read(), f"{self.game_id}.jpg")

        return qr_code.file_id


class CreateMultiDeviceGame(BaseModel):
    host_id: UUID
    player_amount: int
