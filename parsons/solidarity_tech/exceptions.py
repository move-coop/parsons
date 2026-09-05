"""Exceptions raised by Parsons Solidarity Tech API Connector."""

import requests
from requests.exceptions import HTTPError


class STResponseError(HTTPError):
    """Base exception for all Solidarity Tech response errors."""

    def __init__(
        self, message: str | None = None, *args, err_msg: str, response: requests.Response, **kwargs
    ) -> None:
        if response.status_code:
            err_msg += f" (Status Code {response.status_code})"
        if message:
            err_msg += f" -- {message}"
        super().__init__(err_msg, *args, **kwargs)


class STFailedResponseError(STResponseError):
    """Status code indicates a known failure."""

    def __init__(
        self, message: str | None = None, *args, response: requests.Response, **kwargs
    ) -> None:
        err_msg = "Request Failed"
        super().__init__(message, *args, err_msg=err_msg, response=response, **kwargs)


class STUnexpectedResponseError(STResponseError):
    """Status code is not expected."""

    def __init__(
        self, message: str | None = None, *args, response: requests.Response, **kwargs
    ) -> None:
        err_msg = "Unexpected Response"
        super().__init__(message, *args, err_msg=err_msg, response=response, **kwargs)
