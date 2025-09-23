from typing import Any, Dict
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.assets.base import BaseObject


@dataclass
class SingleDeviceGame(BaseObject):
    game_id: UUID
    user_id: UUID
    telegram_id: int
    secret_word: str
    player_amount: int
    spy_index: int

    @classmethod
    def from_dict(
            cls,
            data: Dict[str, Any]
    ) -> 'SingleDeviceGame':
        return cls(
            game_id=UUID(data.get("game_id")),
            user_id=UUID(data.get("user_id")),
            telegram_id=data.get("telegram_id"),
            secret_word=data.get("secret_word"),
            player_amount=data.get("player_amount"),
            spy_index=data.get("spy_index")
        )
