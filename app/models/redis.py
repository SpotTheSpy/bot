from abc import ABC
from typing import ClassVar, TYPE_CHECKING, Any, Dict, Optional, Self

from app.models.abstract import AbstractModel

if TYPE_CHECKING:
    from app.controllers.redis import RedisController
else:
    RedisController = Any


class AbstractRedisModel(AbstractModel, ABC):
    key: ClassVar[str]

    _controller: Optional['RedisController'] = None

    @property
    def controller(self) -> 'RedisController':
        if self._controller is None:
            raise ValueError("Controller is not set")
        return self._controller

    @classmethod
    def from_json_and_controller(
            cls,
            data: Dict[str, Any],
            *,
            controller: 'RedisController',
            **kwargs: Any
    ) -> Self | None:
        value = cls.from_json(data, **kwargs)

        if value is not None:
            value._controller = controller

        return value

    async def save(self) -> None:
        await self.controller.set(self)

    async def clear(self) -> None:
        await self.controller.remove(self.primary_key)
