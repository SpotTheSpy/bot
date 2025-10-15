import json
from typing import Any, Tuple, List, Generic, TypeVar, Type, Callable, Dict

from redis.asyncio import Redis

from app.models.redis import AbstractRedisModel
from app.parameters import Parameters

T = TypeVar('T', bound=AbstractRedisModel)


class RedisController(Generic[T]):
    """
    Redis controller class.

    Provides control over values inside a Redis database,
    represented as a JSON of some AbstractRedisModel instance.

    Please make sure to select a generic model after a class name definition,
    otherwise any method execution may result in an error.

    Example usage:

    '''
    controller = RedisController[RedisModel](...)
    '''
    """

    def __init__(
            self,
            redis: Redis,
            *,
            default_key: str | None = None
    ) -> None:
        """
        Initialize Redis controller instance.

        :param redis: Redis connection instance.
        :param default_key: Default controller key to unify resulted keys.
        """

        self._redis: Redis = redis
        self._default_key: str = default_key or Parameters.DEFAULT_REDIS_KEY

    @property
    def object_class(self) -> Type[T]:
        """
        Class of an object, selected as a generic.

        :raise ValueError: If generic object class is not selected.
        :return: Object class.
        """

        if not hasattr(self, "__orig_class__"):
            raise ValueError("Generic redis object class is not set")
        classes = getattr(self, "__orig_class__").__args__
        if not classes:
            raise ValueError("Generic redis object class is not set")

        return classes[0]

    @property
    def key(self) -> str:
        """
        Object class Redis key, required in every Redis model class to define key structure.

        :raise ValueError: If the key is not defined.
        :return: Object class Redis key.
        """

        try:
            return self.object_class.key
        except NameError:
            raise ValueError("Key attribute in generic redis object class is not set")

    async def set(
            self,
            value: T
    ) -> None:
        """
        Set new value by a primary key as a JSON representation.

        :param value: Value to be set.
        """

        await self._set(str(value.primary_key), value.to_json())

    async def get(
            self,
            primary_key: Any,
            from_json_method: Callable[..., T] | None = None,
            **kwargs: Any
    ) -> T | None:
        """
        Retrieve value by primary key.

        :param primary_key: Primary key for the value to be retrieved.
        :param from_json_method: Method for converting JSON representation of value to a Redis object.
        :param kwargs: Keyword arguments for convertion method.
        :return: Value if exists, None otherwise.
        """

        value: Dict[str, Any] | None = await self._get(str(primary_key))

        if from_json_method is None:
            from_json_method = self.object_class.from_json_and_controller

        return None if value is None else from_json_method(
            value,
            controller=self,
            **kwargs
        )

    async def exists(
            self,
            primary_key: Any
    ) -> bool:
        """
        Check if primary key exists.

        :param primary_key: Primary key to be checked.
        :return: True if exists, False otherwise.
        """

        return await self._exists(str(primary_key))

    async def remove(
            self,
            primary_key: Any
    ) -> None:
        """
        Remove value by primary key.

        :param primary_key: Primary key for the value to be removed.
        """

        await self._remove(str(primary_key))

    async def all(
            self,
            *,
            limit: int | None = None,
            offset: int | None = None,
            count: int | None = None,
            from_json_method: Callable[..., T] | None = None,
            **kwargs: Any
    ) -> Tuple[T, ...]:
        """
        Retrieve all values with limit and offset.

        :param limit: Limit of values to be retrieved, defaults to 100.
        :param offset: Offset of values to be retrieved, defaults to 0.
        :param count: Count of values to be retrieved on each iteration, defaults to 100.
        :param from_json_method: Method for converting JSON representation of value to a Redis object.
        :param kwargs: Keyword arguments for convertion method.
        :return: Tuple of Redis objects.
        """

        values: List[T] = []

        if from_json_method is None:
            from_json_method = self.object_class.from_json_and_controller

        for key in await self._get_keys(limit=limit, offset=offset, count=count):
            value = from_json_method(
                await self._get(key, exact_key=True),
                controller=self,
                **kwargs
            )

            if value is None:
                continue

            values.append(value)

        return tuple(values)

    def _key(self, *args: str, exact: bool = False) -> str:
        """
        Generate a Redis key using a sequence of args.

        :param args: Arguments to be converted to a Redis key.
        :param exact: Whether to omit default and Redis object class keys on the prefix.
        :return: Generated Redis key.
        """

        keys: Tuple[str, ...] = (*args,) if exact else (self._default_key, self.key, *args)
        return ":".join(keys)

    def _pattern(self, *, exact: bool = False) -> str:
        """
        Generate a Redis pattern using a sequence of args.

        :param exact: Whether to omit default and Redis object class keys on the prefix.
        :return: Generated Redis pattern.
        """

        return "" if exact else f"*{self._default_key}:{self.key}*"

    async def _set(self, key: str, value: Any, *, exact_key: bool = False) -> None:
        """
        Set value by a primary key and JSON-Serializable value.

        :param key: Primary key.
        :param value: Value to be set.
        :param exact_key: Whether to omit default and Redis object class keys on the prefix.
        """

        await self._redis.set(self._key(key, exact=exact_key), json.dumps(value))

    async def _get(self, key: str, *, exact_key: bool = False) -> Any:
        """
       Retrieve a JSON-Serializable value by a primary key.

       :param key: Primary key.
       :param exact_key: Whether to omit default and Redis object class keys on the prefix.
       :return: JSON-Serializable value if exists, None otherwise.
       """

        serialized: str = await self._redis.get(self._key(key, exact=exact_key))
        return json.loads(serialized) if serialized is not None else None

    async def _exists(self, key: str, *, exact_key: bool = False) -> bool:
        """
        Check if a primary key exists.

        :param key: Primary key.
        :param exact_key: Whether to omit default and Redis object class keys on the prefix.
        :return: True if exists, False otherwise.
        """

        return bool(await self._redis.exists(self._key(key, exact=exact_key)))

    async def _remove(self, key: str, *, exact_key: bool = False) -> None:
        """
        Remove value by a primary key.

        :param key: Primary key.
        :param exact_key: Whether to omit default and Redis object class keys on the prefix.
        """

        await self._redis.delete(self._key(key, exact=exact_key))

    async def _get_keys(
            self,
            *,
            pattern: str | None = None,
            limit: int | None = None,
            offset: int | None = None,
            count: int | None = None
    ) -> Tuple[str, ...]:
        """
        Retrieve all keys with Redis object pattern, limit and offset.

        :param pattern: Pattern select keys, if None, a default pattern is used.
        :param limit: Limit of keys to be retrieved, defaults to 100.
        :param offset: Offset of keys to be retrieved, defaults to 0.
        :param count: Count of keys to be retrieved on each iteration, defaults to 100.
        :return: Tuple of Redis keys.
        """

        if limit is None:
            limit = 100
        if offset is None:
            offset = 0
        if count is None:
            count = 100

        cursor: int = 0
        skipped: int = 0
        collected: List[str] = []

        while True:
            cursor, keys = await self._redis.scan(
                cursor=cursor,
                match=f"*{pattern}*" if pattern is not None else self._pattern(),
                count=count
            )

            for key in keys:
                if skipped < offset:
                    skipped += 1
                    continue
                if len(collected) < limit:
                    collected.append(key.decode())
                if len(collected) >= limit:
                    return tuple(collected)

            if cursor == 0:
                break

        return tuple(collected)
