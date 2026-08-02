import requests
from requests.exceptions import HTTPError


class STUnexpectedResponseError(HTTPError):
    """Status code is not expected."""

    def __init__(self, message: str | None = None, *, response: requests.Response) -> None:
        err_msg = "Unexpected Response"
        if response and response.status_code:
            err_msg += f" (Status Code {response.status_code})"
        if message:
            err_msg += f" -- {message}"
        super().__init__(err_msg, response=response)


class STFailedResponseError(HTTPError):
    """Status code indicates a known failure."""

    def __init__(self, message: str, *, response: requests.Response) -> None:
        err_msg = "Request Failed"
        if response and response.status_code:
            err_msg += f" (Status Code {response.status_code})"
        if message:
            err_msg += f" -- {message}"
        super().__init__(err_msg, response=response)
