import asyncio
from abc import ABC
from functools import wraps
from typing import Callable, Any, Dict

from aiohttp import ClientConnectorError, ClientSession, ClientResponse

from config import config


class AttributedDict(dict):
    """
    Dictionary subclass that allows accessing values as attributes.
    """

    def __init__(
            self,
            dictionary: dict,
            **kwargs
    ) -> None:
        """
        Initialize AttributedDict.

        :param dictionary: Dictionary to initialize.
        :param kwargs: Additional keyword arguments.
        """

        super().__init__(dictionary, **kwargs)

        for key, value in dictionary.items():
            setattr(self, str(key), self.__process_value__(value))

    def __getattr__(
            self,
            item: str
    ) -> Any:
        """
        Get attribute value from dictionary.
        :param item: Attribute to get.
        :return: Attribute value.
        """

        return self.__dict__.get(item)

    def __process_value__(
            self,
            value: Any
    ) -> Any:
        """
        Convert dictionary value to attributed value.

        If value is an instance of dictionary, converts it to an AttributedDict.
        If value is a list, applies recursively to each item in it.
        Otherwise, returns the same value.

        :param value: Value to convert.
        :return: Converted value.
        """

        if isinstance(value, dict):
            return AttributedDict(value)

        if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
            return [self.__process_value__(item) for item in value]

        return value


class APIController(ABC):
    def __init__(
            self,
            cycles: int | None = None,
            timeout: int | None = None,
            **kwargs: Any
    ) -> None:
        """
        API controller class.

        Base class for building API controllers, provides methods for sending basic HTTP requests.

        :param config: Configuration model for API controllers.
        :param cycles: Number of retries to resend request if an ASGI server is temporarily unavailable.
        :param timeout: Timeout of every retry in seconds.
        :param kwargs: Additional headers.
        """

        self._cycles = cycles or config.api_retry_cycles
        self._timeout = timeout or config.api_retry_timeout
        self._headers: Dict[str, Any] = {"API-Key": config.api_key, **kwargs}

    async def _post(
            self,
            path: str,
            **kwargs
    ) -> AttributedDict:
        """
        Send a POST request to an API endpoint.

        :param path: API endpoint path.
        :param kwargs: Additional arguments.
        :return: API response as an AttributedDict.
        """

        @self._apply_resend
        async def __post() -> AttributedDict:
            headers = self._headers.copy()
            headers.update(kwargs.get("headers", {}))

            client_session = ClientSession(headers=headers)

            async with client_session as session:
                request = session.post(
                    f"{config.api_url}/{path}",
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
        """
        Send a GET request to an API endpoint.

        :param path: API endpoint path.
        :param kwargs: Additional arguments.
        :return: API response as an AttributedDict.
        """

        @self._apply_resend
        async def __get() -> AttributedDict:
            headers = self._headers.copy()
            headers.update(kwargs.get("headers", {}))

            client_session = ClientSession(headers=headers)

            async with client_session as session:
                request = session.get(
                    f"{config.api_url}/{path}",
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
        """
        Send a PUT request to an API endpoint.

        :param path: API endpoint path.
        :param kwargs: Additional arguments.
        :return: API response as an AttributedDict.
        """

        @self._apply_resend
        async def __put() -> AttributedDict:
            headers = self._headers.copy()
            headers.update(kwargs.get("headers", {}))

            client_session = ClientSession(headers=headers)

            async with client_session as session:
                request = session.put(
                    f"{config.api_url}/{path}",
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
        """
        Send a DELETE request to an API endpoint.

        :param path: API endpoint path.
        :param kwargs: Additional arguments.
        :return: API response as an AttributedDict.
        """

        @self._apply_resend
        async def __delete() -> AttributedDict:
            headers = self._headers.copy()
            headers.update(kwargs.get("headers", {}))

            client_session = ClientSession(headers=headers)

            async with client_session as session:
                request = session.delete(
                    f"{config.api_url}/{path}",
                    **kwargs
                )

                async with request as response:
                    return await self._construct_response(response)

        return await __delete()

    def _apply_resend(
            self,
            func: Callable
    ) -> Callable:
        """
        Apply retrying process for methods if an endpoint is temporarily unavailable.

        :param func: Function to apply retrying process.
        :return: Result function.
        """

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
        """
        Construct an AttributedDict object from response.

        Converts JSON response to an AttributedDict and additionally sets a status code attribute.
        :param response: Client response object.
        :return: AttributedDict object.
        """

        json_response: dict = await response.json() or {}
        json_response.update({"status_code": response.status})

        return AttributedDict(json_response)
