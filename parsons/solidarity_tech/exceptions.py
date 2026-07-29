import requests
from requests.exceptions import HTTPError


class STUnexpectedResponseCodeError(HTTPError):
    """Status code is not expected."""

    def __init__(self, res: requests.Response) -> None:
        super()
        self.status_code = res.status_code

    def __str__(self):
        return f"Received unexpected response. (Status Code: {self.status_code})"
