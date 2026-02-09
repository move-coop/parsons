import logging
import urllib.parse
from typing import Any, Literal

import requests
from requests import request as _request
from requests.exceptions import HTTPError
from simplejson.errors import JSONDecodeError

from parsons import Table

logger = logging.getLogger(__name__)


class APIConnector:
    """
    The API Connector is a low level class for API requests that other connectors can utilize.

    It is understood that there are many standards for REST APIs and it will be difficult to create a universal
    connector. The goal of this class is create series of utilities that can be mixed and matched to, hopefully, meet
    the needs of the specific API.

    Args:
        uri (str): The base uri for the api. Must include a trailing '/' (e.g.
            ``http://myapi.com/v1/``).
        headers (dict, optional): The request headers. Defaults to None.
        auth (dict, optional): The request authorization parameters. Defaults to None.
        pagination_key (str, optional): The name of the key in the response json where the pagination url is
            located. Required for pagination. Defaults to None.
        data_key (str, optional): The name of the key in the response json where the data is contained.
            Required if the data is nested in the response json. Defaults to None.

    Returns:
        APIConnector class

    """

    def __init__(self, uri, headers=None, auth=None, pagination_key=None, data_key=None):
        # Add a trailing slash if its missing
        if not uri.endswith("/"):
            uri = uri + "/"

        self.uri = uri
        self.headers = headers
        self.auth = auth
        self.pagination_key = pagination_key
        self.data_key = data_key

    def request(
        self,
        url: str,
        req_type: Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"],
        json: dict = None,
        data: str | bytes | dict | None = None,
        params: dict | None = None,
    ):
        """
        Base request using requests libary.

        Args:
            url (str): The url request string; if ``url`` is a relative URL, it will be joined with the ``uri`` of
                the ``APIConnector`; if ``url`` is an absolute URL, it will be used as is.
            req_type (Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"]): The request type.
            json (dict, optional): The payload of the request object. By using json, it will automatically serialize
                the dictionary. Defaults to None.
            data (str | bytes | dict | None, optional): The payload of the request object.
                Use instead of json in some instances. Defaults to None.
            params (dict | None, optional): The parameters to append to the url
                (e.g. http://myapi.com/things?id=1). Defaults to None.

        Returns:
            requests response

        """
        full_url = urllib.parse.urljoin(self.uri, url)

        return _request(
            req_type,
            full_url,
            headers=self.headers,
            auth=self.auth,
            json=json,
            data=data,
            params=params,
        )

    def _handle_request_with_response(
        self,
        method: Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"],
        url: str,
        success_codes: list[int] | None = None,
        **kwargs,
    ):
        """Internal helper to handle shared logic for POST, PUT, PATCH, and DELETE."""
        r = self.request(url, method, **kwargs)
        self.validate_response(r)

        if success_codes is None:
            success_codes = [200, 201, 202, 204]

        # Check for a valid success code. Some APIs return messages with the
        # success code and some do not. Be able to account for both of these types.
        if r.status_code in success_codes:
            return r.json() if self.json_check(r) else r.status_code
        return r.status_code

    def get_request(
        self,
        url: str,
        params: dict | None = None,
        return_format: Literal["json", "content"] = "json",
    ):
        """
        Make a GET request.

        Args:
            url (str): A complete and valid url for the api request.
            params (dict | None, optional): The request parameters. Defaults to None.
            return_format (Literal["json", "content"], optional): Literal["json", "content"], optional The format to
                return the data in. json is default. Defaults to "json".

        Returns:
            A requests response object

        """
        r = self.request(url, "GET", params=params)
        self.validate_response(r)

        if return_format == "json":
            logger.debug(r.json())
            return r.json()
        elif return_format == "content":
            return r.content
        else:
            raise RuntimeError(f"{return_format} is not a valid format, change to json or content")

    def post_request(
        self,
        url: str,
        params: dict | None = None,
        data: str | bytes | None = None,
        json: dict | None = None,
        success_codes: list[int] | None = None,
    ) -> Any | int:
        """
        Make a POST request.

        Args:
            url (str): A complete and valid url for the api request.
            params (dict | None, optional): The request parameters. Defaults to None.
            data (str | bytes | None, optional): | bytes, optional A data object to post. Defaults to None.
            json (dict | None, optional): A JSON object to post. Defaults to None.
            success_codes (list[int] | None, optional): The expected success code to be returned.
                If not provided, accepts 200, 201, 202, and 204. Defaults to None.

        Returns:
            Any | int: Response json or status code on failure.

        """
        return self._handle_request_with_response(
            "POST", url, success_codes, params=params, data=data, json=json
        )

    def delete_request(
        self, url: str, params: dict | None = None, success_codes: list[int] | None = None
    ):
        """
        Make a DELETE request.

        Args:
            url (str): A complete and valid url for the api request.
            params (dict | None, optional): The request parameters. Defaults to None.
            success_codes (list[int] | None, optional): The expected success codes to be returned.
                If not provided, accepts 200, 201, 204. Defaults to None.

        Returns:
            A requests response object or status code

        """
        return self._handle_request_with_response("DELETE", url, success_codes, params=params)

    def put_request(
        self,
        url: str,
        data: str | bytes | None = None,
        json: dict | None = None,
        params: dict | None = None,
        success_codes: list[int] | None = None,
    ):
        """
        Make a PUT request.

        Args:
            url (str): A complete and valid url for the api request.
            data (str | bytes | None, optional): | bytes, optional A data object to post. Defaults to None.
            json (dict | None, optional): A JSON object to post. Defaults to None.
            params (dict | None, optional): The request parameters. Defaults to None.
            success_codes (list[int] | None, optional): The expected success codes to be returned.
                If not provided, accepts 200, 201, 204. Defaults to None.

        Returns:
            A requests response object

        """
        return self._handle_request_with_response(
            "PUT", url, success_codes, params=params, data=data, json=json
        )

    def patch_request(
        self,
        url: str,
        params: dict | None = None,
        data: str | bytes | None = None,
        json: dict | None = None,
        success_codes: list[int] | None = None,
    ):
        """
        Make a PATCH request.

        Args:
            url (str): A complete and valid url for the api request.
            params (dict | None, optional): The request parameters. Defaults to None.
            data (str | bytes | None, optional): | file, optional A data object to post. Defaults to None.
            json (dict | None, optional): A JSON object to post. Defaults to None.
            success_codes (list[int] | None, optional): The expected success codes to be returned.
                If not provided, accepts 200, 201, and 204. Defaults to None.

        Returns:
            A requests response object

        """
        return self._handle_request_with_response(
            "PATCH", url, success_codes, params=params, data=data, json=json
        )

    def validate_response(self, resp: requests.Response):
        """
        Validate that the response is not an error code.

        If it is, then raise an error and display the error message.

        Args:
            resp (requests.Response)

        """
        if resp.status_code >= 400:
            # Get the most descriptive error detail available
            detail = resp.reason or resp.text or ""
            message = f"HTTP error occurred ({resp.status_code}): {detail}".strip(": ")

            # Append JSON info if present
            if self.json_check(resp):
                message = f"{message}, json: {resp.json()}"

            raise HTTPError(message)

    def data_parse(self, resp):
        """
        Determines if the response json has nested data.

        If it is nested, it just returns the data. This is useful in dealing with requests that might return multiple
        records, while others might return only a single record.

        Args:
            resp: A response dictionary.

        Returns:
            dict: A dictionary of data.

        """
        # TODO: Some response jsons are enclosed in a list. Need to deal with unpacking and/or not assuming that it is going to be a dict.

        # In some instances responses are just lists.
        if isinstance(resp, list):
            return resp

        if self.data_key and isinstance(resp, dict) and self.data_key in resp:
            return resp[self.data_key]
        return resp

    def next_page_check_url(self, resp: dict) -> bool:
        """
        Check to determine if there is a next page.

        This requires that the response json contains a pagination key that is empty if there is not a next page.

        Args:
            resp (dict): A response dictionary.

        Returns:
            bool

        """
        if self.pagination_key and self.pagination_key in resp:
            return bool(resp[self.pagination_key])
        return False

    @staticmethod
    def json_check(resp):
        """Check to see if a response has a json included in it."""
        try:
            resp.json()
        except (JSONDecodeError, ValueError):
            return False
        return True

    @staticmethod
    def convert_to_table(data):
        """Internal method to create a Parsons table from a data element."""
        return Table(data) if type(data) is list else Table([data])
