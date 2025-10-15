from abc import ABC
from typing import ClassVar, TYPE_CHECKING, Any, Dict, Optional, Self

from app.models.abstract import AbstractModel

if TYPE_CHECKING:
    from app.controllers.redis import RedisController
else:
    RedisController = Any


class AbstractRedisModel(AbstractModel, ABC):
    """
    Abstract class for Redis models.

    This is an abstract class for objects which represent specific values in a Redis database.

    Redis key is usually constructed from a default redis key from a controller instance,
    a key class argument unique for every redis model class,
    and a primary key which must be unique for every redis object.

    Value is a JSON-Serialized object by to_json() method.
    """

    key: ClassVar[str]

    _controller: Optional['RedisController'] = None

    @property
    def controller(self) -> 'RedisController':
        """
        Redis controller instance. A private parameter must be set after an object initialization.

        :raise ValueError: If a controller instance is not set.
        :return: Redis controller instance.
        """

        if self._controller is None:
            raise ValueError("Controller is not set")
        return self._controller

    @classmethod
    def from_json_and_controller(
            cls,
            data: Dict[str, Any] | None,
            *,
            controller: 'RedisController',
            **kwargs: Any
    ) -> Self | None:
        """
        Reconstruct a model instance from a JSON-Serialized dictionary and a controller instance.

        :param data: Dictionary to reconstruct a model instance.
        :param controller: Redis controller instance.
        :param kwargs: Any additional JSON-Serializable parameters.
        :return: A model instance if validated successfully, else None.
        """

        value = cls.from_json(data, **kwargs)

        if value is not None:
            value._controller = controller

        return value

    async def save(self) -> None:
        """
        Save a model to Redis.
        """

        await self.controller.set(self)

    async def clear(self) -> None:
        """
        Clear a model from Redis.
        """

        await self.controller.remove(self.primary_key)
