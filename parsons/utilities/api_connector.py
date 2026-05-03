import logging
import urllib.parse
from typing import Any, Literal, overload

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from simplejson.errors import JSONDecodeError

from parsons import Table

logger = logging.getLogger(__name__)


class APIConnector:
    """
    Low level class for API requests that other connectors can utilize.

    It is understood that there are many standards for REST APIs and
    it will be difficult to create a universal connector.
    The goal of this class is create series of utilities that can be
    mixed and matched to, hopefully, meet the needs of the specific API.

    """

    def __init__(
        self,
        uri: str,
        headers: dict | None = None,
        auth: HTTPBasicAuth | None = None,
        pagination_key: str | None = None,
        data_key: str | None = None,
    ) -> None:
        """
        Initialize the APIConnector.

        Args:
            uri:
                The base uri for the api.
                Must include a trailing ``/``.
                E.g. ``http://myapi.com/v1/``.
            headers: The request headers
            auth: The request authorization parameters
            pagination_key:
                The name of the key in the response json
                where the pagination url is located.
                Required for pagination.
            data_key:
                The name of the key in the response json
                where the data is contained.
                Required if the data is nested in the response json.

        """
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
        req_type: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        *,
        json: dict[str, Any] | None = None,
        data: str | bytes | dict | list[tuple] | None = None,
        params: dict[str, str | int] | None = None,
        raise_on_error: bool = True,
        **kwargs,
    ) -> requests.Response:
        """
        Base request using requests libary.

        Args:
            url:
                The url request string.
                If ``url`` is a relative URL,
                it will be joined with the ``uri`` of the ``APIConnector`.
                If ``url`` is an absolute URL,
                it will be used as is.
            req_type: The request type.
            json:
                The payload of the request object.
                By using json, it will automatically serialize the dictionary.
            data:
                The payload of the request object.
                Use instead of json in some instances.
            params:
                The parameters to append to the url.
                E.g. ``http://myapi.com/things?id=1``
            raise_on_error:
                If the request yields an error status code (anything above 400),
                raise an error. In most cases, this should be ``True``,
                however in some cases, if you are looping through data,
                you might want to ignore individual failures.
            `**kwargs`:
                Additional keyword arguments to pass to :func:`requests.request`.

        """
        full_url = urllib.parse.urljoin(self.uri, url)

        resp = requests.request(
            req_type,
            full_url,
            headers=self.headers,
            auth=self.auth,
            json=json,
            data=data,
            params=params,
            **kwargs,
        )

        if raise_on_error:
            self.validate_response(resp)

        return resp

    @overload
    def get_request(
        self,
        url: ...,
        *,
        params: ... = ...,
        return_format: Literal["json"] = "json",
        raise_on_error: ... = ...,
        **kwargs,
    ) -> dict[str, Any]: ...

    @overload
    def get_request(
        self,
        url: ...,
        *,
        params: ... = ...,
        return_format: Literal["content"],
        raise_on_error: ... = ...,
        **kwargs,
    ) -> bytes: ...

    def get_request(
        self,
        url: str,
        *,
        params: dict[str, str | int] | None = None,
        return_format: Literal["json", "content"] = "json",
        raise_on_error: bool = True,
        **kwargs,
    ) -> dict | bytes:
        """
        Make a GET request.

        Args:
            url: A complete and valid url for the api request.
            params: The request parameters.
            raise_on_error:
                If the request yields an error status code (anything above 400),
                raise an error. In most cases, this should be ``True``,
                however in some cases, if you are looping through data,
                you might want to ignore individual failures.
            `**kwargs`:
                Additional keyword arguments to pass to :func:`requests.request`.

        Returns:
            The :meth:`requests.Response.json` from the response if `return_format` is ``json``,
            or :attr:`requests.Response.content` from the response if `return_format` is ``content``.

        Raises:
            RuntimeError: If return_format is not ``json`` or ``content``.

        """
        r = self.request(url, "GET", params=params, raise_on_error=raise_on_error, **kwargs)

        if return_format == "json":
            return r.json()

        if return_format == "content":
            return r.content

        raise RuntimeError(f"{return_format} is not a valid format, change to json or content")

    def post_request(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: str | bytes | dict | list[tuple] | None = None,
        json: dict[str, Any] | None = None,
        success_codes: list[int] | None = None,
        raise_on_error: bool = True,
        **kwargs,
    ) -> dict[str, Any] | int | None:
        """
        Make a POST request.

        Args:
            url: A complete and valid url for the api request
            params: The request parameters
            data: A data object to post
            json: A JSON object to post
            success_codes:
                The expected success code to be returned.
                If not provided, accepts 200, 201, 202, and 204.
            raise_on_error:
                If the request yields an error status code (anything above 400),
                raise an error. In most cases, this should be ``True``,
                however in some cases, if you are looping through data,
                you might want to ignore individual failures.
            `**kwargs`:
                Additional keyword arguments to pass to :func:`requests.request`.

        Returns:
            If successful, json date from :meth:`requests.Response.json`
            or :attr:`requests.Response.status_code` as available.
            ``None`` if the request fails and `raise_on_error` is ``False``.

        """
        r = self.request(
            url,
            "POST",
            params=params,
            data=data,
            json=json,
            raise_on_error=raise_on_error,
            **kwargs,
        )

        # Check for a valid success code for the POST.
        # Some APIs return messages with the success code and some do not.
        # Be able to account for both of these types.
        if success_codes is None:
            success_codes = [200, 201, 202, 204]

        if r.status_code in success_codes:
            if self.json_check(r):
                return r.json()

            return r.status_code

    def delete_request(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        success_codes: list[int] | None = None,
        raise_on_error: bool = True,
        **kwargs,
    ) -> dict[str, Any] | int | None:
        """
        Make a DELETE request.

        Args:
            url: A complete and valid url for the api request
            params: The request parameters
            success_codes:
                The expected success codes to be returned.
                If not provided, accepts 200, 201, 204.
            raise_on_error:
                If the request yields an error status code (anything above 400),
                raise an error. In most cases, this should be ``True``,
                however in some cases, if you are looping through data,
                you might want to ignore individual failures.
            `**kwargs`:
                Additional keyword arguments to pass to :func:`requests.request`.

        Returns:
            If successful, json date from :meth:`requests.Response.json`
            or :attr:`requests.Response.status_code` as available.
            ``None`` if the request fails and `raise_on_error` is ``False``.

        """
        r = self.request(url, "DELETE", params=params, raise_on_error=raise_on_error, **kwargs)

        # Check for a valid success code for the POST.
        # Some APIs return messages with the success code and some do not.
        # Be able to account for both of these types.
        if success_codes is None:
            success_codes = [200, 201, 202, 204]

        if r.status_code in success_codes:
            if self.json_check(r):
                return r.json()

            return r.status_code

    def put_request(
        self,
        url: str,
        *,
        data: str | bytes | dict | list[tuple] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        success_codes: list[int] | None = None,
        raise_on_error: bool = True,
        **kwargs,
    ) -> dict[str, Any] | int | None:
        """
        Make a PUT request.

        Args:
            url: A complete and valid url for the api request
            data: A data object to post
            json: A JSON object to post
            params: The request parameters
            success_codes:
                The expected success codes to be returned.
                If not provided, accepts 200, 201, 204.
            raise_on_error:
                If the request yields an error status code (anything above 400),
                raise an error. In most cases, this should be ``True``,
                however in some cases, if you are looping through data,
                you might want to ignore individual failures.
            `**kwargs`:
                Additional keyword arguments to pass to :func:`requests.request`.

        Returns:
            If successful, json date from :meth:`requests.Response.json`
            or :attr:`requests.Response.status_code` as available.
            ``None`` if the request fails and `raise_on_error` is ``False``.

        """
        r = self.request(
            url, "PUT", params=params, data=data, json=json, raise_on_error=raise_on_error, **kwargs
        )

        # Check for a valid success code for the POST.
        # Some APIs return messages with the success code and some do not.
        # Be able to account for both of these types.
        if success_codes is None:
            success_codes = [200, 201, 202, 204]

        if r.status_code in success_codes:
            if self.json_check(r):
                return r.json()

            return r.status_code

    def patch_request(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: str | bytes | dict | list[tuple] | None = None,
        json: dict[str, Any] | None = None,
        success_codes: list[int] | None = None,
        raise_on_error: bool = True,
        **kwargs,
    ) -> dict[str, Any] | int | None:
        """
        Make a PATCH request.

        Args:
            url: A complete and valid url for the api request
            params: The request parameters
            data: A data object to post
            json: A JSON object to post
            success_codes:
                The expected success codes to be returned.
                If not provided, accepts 200, 201, and 204.
            raise_on_error:
                If the request yields an error status code (anything above 400),
                raise an error. In most cases, this should be ``True``,
                however in some cases, if you are looping through data,
                you might want to ignore individual failures.
            `**kwargs`:
                Additional keyword arguments to pass to :func:`requests.request`.

        Returns:
            If successful, json date from :meth:`requests.Response.json`
            or :attr:`requests.Response.status_code` as available.
            ``None`` if the request fails and `raise_on_error` is ``False``.

        """
        r = self.request(
            url,
            "PATCH",
            params=params,
            data=data,
            json=json,
            raise_on_error=raise_on_error,
            **kwargs,
        )

        # Check for a valid success code for the POST.
        # Some APIs return messages with the success code and some do not.
        # Be able to account for both of these types.
        if success_codes is None:
            success_codes = [200, 201, 202, 204]

        if r.status_code in success_codes:
            if self.json_check(r):
                return r.json()

            return r.status_code

    def validate_response(self, resp: requests.Response) -> None:
        """
        Validate that the response is not an error code.

        If it is, then raise an error and display the error message.

        """
        try:
            resp.raise_for_status()

        except HTTPError as e:
            message = f"Code: {resp.status_code}; URL: {resp.url}"

            if resp.reason:
                message = f"{message}; Reason: {resp.reason}"

            elif resp.text:
                message = f"{message}; Text: {resp.text}"

            # Some errors return JSONs with useful info about the error.
            if self.json_check(resp):
                message = f"{message}; JSON: {resp.json()}"

            raise HTTPError(message) from e

    @overload
    def data_parse(self, resp: dict) -> dict: ...

    @overload
    def data_parse(self, resp: list) -> list: ...

    def data_parse(self, resp: dict | list) -> dict | list:
        """
        Determines if the response json has nested data.

        If it is nested, it just returns the data.
        This is useful in dealing with requests that might return multiple records,
        while others might return only a single record.

        """
        # TODO: Some response jsons are enclosed in a list.
        # Need to deal with unpacking and/or not assuming that it is going to be a dict.

        # In some instances responses are just lists.
        if isinstance(resp, list):
            return resp

        if self.data_key and self.data_key in resp:
            return resp[self.data_key]

        return resp

    # There are many different ways in which APIs indicate whether there is a next page
    # of data following the initial request. The goal is build out a series of utilities
    # that mean most of the most common use cases.

    def next_page_check_url(self, resp: dict) -> bool:
        """
        Check to determine if there is a next page.

        This requires that the response json contains a pagination key
        that is empty if there is not a next page.

        """
        if self.pagination_key and self.pagination_key in resp:
            return bool(resp[self.pagination_key])

        return False

    def json_check(self, resp: requests.Response) -> bool:
        """Check to see if a response has a json included in it."""
        try:
            resp.json()
            return True

        except JSONDecodeError:
            return False

    def convert_to_table(self, data: list | Any) -> Table:
        """Internal method to create a Parsons table from a data element."""
        return Table(data) if isinstance(data, list) else Table([data])
