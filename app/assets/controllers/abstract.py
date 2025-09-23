import asyncio
from abc import ABC
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Any, Dict

from aiohttp import ClientConnectorError, ClientSession, ClientResponse


@dataclass
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
    _CYCLES: int = 3
    _TIMEOUT: int = 1

    def __init__(
            self,
            api_config: APIConfig
    ) -> None:
        self.base_url = api_config.base_url
        self.api_key = api_config.api_key

        self._headers: Dict[str, Any] = {"API-Key": self.api_key}

    @staticmethod
    def apply_resend(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
                *args,
                **kwargs
        ) -> Any:
            connection_error: ClientConnectorError | None = None

            for _ in range(APIController._CYCLES):
                try:
                    return await func(*args, **kwargs)
                except ClientConnectorError as error:
                    connection_error = error
                    await asyncio.sleep(APIController._TIMEOUT)

            raise connection_error

        return wrapper

    def update_headers(
            self,
            headers: Dict[str, Any] | None = None,
            **kwargs: Any
    ) -> None:
        if headers is not None:
            kwargs.update(headers)

        self._headers.update(kwargs)

    @apply_resend
    async def _post(
            self,
            path: str,
            **kwargs
    ) -> AttributedDict:
        headers = self._headers.copy()
        headers.update(kwargs.get("headers", {}))

        client_session = ClientSession(headers=headers)

        async with client_session as session:
            request = session.post(
                f"{self.base_url}/{path}",
                **kwargs
            )

            async with request as response:
                return await self.construct_response(response)

    @apply_resend
    async def _get(
            self,
            path: str,
            **kwargs
    ) -> AttributedDict:
        headers = self._headers.copy()
        headers.update(kwargs.get("headers", {}))

        client_session = ClientSession(headers=headers)

        async with client_session as session:
            request = session.get(
                f"{self.base_url}/{path}",
                **kwargs
            )

            async with request as response:
                return await self.construct_response(response)

    @apply_resend
    async def _put(
            self,
            path: str,
            **kwargs
    ) -> AttributedDict:
        headers = self._headers.copy()
        headers.update(kwargs.get("headers", {}))

        client_session = ClientSession(headers=headers)

        async with client_session as session:
            request = session.put(
                f"{self.base_url}/{path}",
                **kwargs
            )

            async with request as response:
                return await self.construct_response(response)

    @staticmethod
    async def construct_response(response: ClientResponse) -> AttributedDict:
        json_response: dict = await response.json() or {}
        json_response.update({"status_code": response.status})

        return AttributedDict(json_response)
