import asyncio
from abc import ABC
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Any, Dict

from aiohttp import ClientConnectorError, ClientSession, ClientResponse

from app.parameters import Parameters


@dataclass(frozen=True)
class APIConfig:
    base_url: str
    api_key: str


class AttributedDict(dict):
    def __init__(
            self,
            dictionary: dict,
            **kwargs
    ) -> None:
        super().__init__(dictionary, **kwargs)

        for key, value in dictionary.items():
            setattr(self, str(key), self.__process_value__(value))

    def __getattr__(
            self,
            item: str
    ) -> Any:
        return self.__dict__.get(item)

    def __process_value__(
            self,
            value: Any
    ) -> Any:
        if isinstance(value, dict):
            return AttributedDict(value)

        if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
            return [self.__process_value__(item) for item in value]

        return value


class APIController(ABC):
    def __init__(
            self,
            config: APIConfig,
            *,
            cycles: int | None = None,
            timeout: int | None = None
    ) -> None:
        self._config = config
        self._cycles = cycles or Parameters.DEFAULT_API_RETRY_CYCLES
        self._timeout = timeout or Parameters.DEFAULT_API_RETRY_TIMEOUT
        self._headers: Dict[str, Any] = {"API-Key": self._config.api_key}

    def update_headers(
            self,
            headers: Dict[str, Any] | None = None,
            **kwargs: Any
    ) -> None:
        if headers is not None:
            kwargs.update(headers)

        self._headers.update(kwargs)

    async def _post(
            self,
            path: str,
            **kwargs
    ) -> AttributedDict:
        @self._apply_resend
        async def __post() -> AttributedDict:
            headers = self._headers.copy()
            headers.update(kwargs.get("headers", {}))

            client_session = ClientSession(headers=headers)

            async with client_session as session:
                request = session.post(
                    f"{self._config.base_url}/{path}",
                    **kwargs
                )

                async with request as response:
                    return await self._construct_response(response)

        return await __post()

    async def _get(
            self,
            path: str,
            **kwargs
    ) -> AttributedDict:
        @self._apply_resend
        async def __get() -> AttributedDict:
            headers = self._headers.copy()
            headers.update(kwargs.get("headers", {}))

            client_session = ClientSession(headers=headers)

            async with client_session as session:
                request = session.get(
                    f"{self._config.base_url}/{path}",
                    **kwargs
                )

                async with request as response:
                    return await self._construct_response(response)

        return await __get()

    async def _put(
            self,
            path: str,
            **kwargs
    ) -> AttributedDict:
        @self._apply_resend
        async def __put() -> AttributedDict:
            headers = self._headers.copy()
            headers.update(kwargs.get("headers", {}))

            client_session = ClientSession(headers=headers)

            async with client_session as session:
                request = session.put(
                    f"{self._config.base_url}/{path}",
                    **kwargs
                )

                async with request as response:
                    return await self._construct_response(response)

        return await __put()

    async def _delete(
            self,
            path: str,
            **kwargs
    ) -> AttributedDict:
        @self._apply_resend
        async def __delete() -> AttributedDict:
            headers = self._headers.copy()
            headers.update(kwargs.get("headers", {}))

            client_session = ClientSession(headers=headers)

            async with client_session as session:
                request = session.delete(
                    f"{self._config.base_url}/{path}",
                    **kwargs
                )

                async with request as response:
                    return await self._construct_response(response)

        return await __delete()

    def _apply_resend(
            self,
            func: Callable
    ) -> Callable:
        @wraps(func)
        async def wrapper(
                *args,
                **kwargs
        ) -> Any:
            connection_error: ClientConnectorError | None = None

            for _ in range(self._cycles):
                try:
                    return await func(*args, **kwargs)
                except ClientConnectorError as error:
                    connection_error = error
                    await asyncio.sleep(self._timeout)

            raise connection_error

        return wrapper

    @staticmethod
    async def _construct_response(response: ClientResponse) -> AttributedDict:
        json_response: dict = await response.json() or {}
        json_response.update({"status_code": response.status})

        return AttributedDict(json_response)
