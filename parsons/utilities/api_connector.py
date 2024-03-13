from requests import request as _request
from requests.exceptions import HTTPError
import logging
import urllib.parse
from simplejson.errors import JSONDecodeError

logger = logging.getLogger(__name__)


class APIConnector(object):
    """
    The API Connector is a low level class for API requests that other connectors
    can utilize. It is understood that there are many standards for REST APIs and it will be
    difficult to create a universal connector. The goal of this class is create series
    of utilities that can be mixed and matched to, hopefully, meet the needs of the specific
    API.

    `Args:`
        uri: str
            The base uri for the api. Must include a trailing '/' (e.g. ``http://myapi.com/v1/``)
        headers: dict
            The request headers
        auth: dict
            The request authorization parameters
        pagination_key: str
            The name of the key in the response json where the pagination url is
            located. Required for pagination.
        data_key: str
            The name of the key in the response json where the data is contained. Required
            if the data is nested in the response json
    `Returns`:
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

    def request(self, url, req_type, json=None, data=None, params=None):
        """
        Base request using requests libary.

        `Args:`
            url: str
                The url request string; if ``url`` is a relative URL, it will be joined with
                the ``uri`` of the ``APIConnector`; if ``url`` is an absolute URL, it will
                be used as is.
            req_type: str
                The request type. One of GET, POST, PATCH, DELETE, OPTIONS
            json: dict
                The payload of the request object. By using json, it will automatically
                serialize the dictionary
            data: str or byte or dict
                The payload of the request object. Use instead of json in some instances.
            params: dict
                The parameters to append to the url (e.g. http://myapi.com/things?id=1)
            raise_on_error:
                If the request yields an error status code (anything above 400), raise an
                error. In most cases, this should be True, however in some cases, if you
                are looping through data, you might want to ignore individual failures.

        `Returns:`
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

    def get_request(self, url, params=None):
        """
        Make a GET request.

        Args:
            url: str
                A complete and valid url for the api request
            params: dict
                The request parameters
        Returns:
                A requests response object
        """

        r = self.request(url, "GET", params=params)
        self.validate_response(r)
        logger.debug(r.json())

        return r.json()

    def post_request(
        self, url, params=None, data=None, json=None, success_codes=[200, 201, 202, 204]
    ):
        """
        Make a POST request.

        `Args:`
            url: str
                A complete and valid url for the api request
            params: dict
                The request parameters
            data: str or file
                A data object to post
            json: dict
                A JSON object to post
            success_code: int
                The expected success code to be returned
        `Returns:`
            A requests response object
        """

        r = self.request(url, "POST", params=params, data=data, json=json)

        # Validate the response and lift up an errors.
        self.validate_response(r)

        # Check for a valid success code for the POST. Some APIs return messages with the
        # success code and some do not. Be able to account for both of these types.
        if r.status_code in success_codes:
            if self.json_check(r):
                return r.json()
            else:
                return r.status_code

    def delete_request(self, url, params=None, success_codes=[200, 201, 204]):
        """
        Make a DELETE request.

        Args:
            url: str
                A complete and valid url for the api request
            params: dict
                The request parameters
            success_codes: int
                The expected success codes to be returned
        Returns:
                A requests response object or status code
        """

        r = self.request(url, "DELETE", params=params)

        self.validate_response(r)

        # Check for a valid success code for the POST. Some APIs return messages with the
        # success code and some do not. Be able to account for both of these types.
        if r.status_code in success_codes:
            if self.json_check(r):
                return r.json()
            else:
                return r.status_code

    def put_request(self, url, data=None, json=None, params=None, success_codes=[200, 201, 204]):
        """
        Make a PUT request.

        Args:
            url: str
                A complete and valid url for the api request
            params: dict
                The request parameters
            data: str or file
                A data object to post
            json: dict
                A JSON object to post
        Returns:
                A requests response object
        """

        r = self.request(url, "PUT", params=params, data=data, json=json)

        self.validate_response(r)

        if r.status_code in success_codes:
            if self.json_check(r):
                return r.json()
            else:
                return r.status_code

    def patch_request(self, url, params=None, data=None, json=None, success_codes=[200, 201, 204]):
        """
        Make a PATCH request.

        `Args:`
            url: str
                A complete and valid url for the api request
            params: dict
                The request parameters
            data: str or file
                A data object to post
            json: dict
                A JSON object to post
            success_codes: int
                The expected success codes to be returned
        `Returns:`
            A requests response object
        """

        r = self.request(url, "PATCH", params=params, data=data, json=json)

        self.validate_response(r)

        # Check for a valid success code for the POST. Some APIs return messages with the
        # success code and some do not. Be able to account for both of these types.
        if r.status_code in success_codes:
            if self.json_check(r):
                return r.json()
            else:
                return r.status_code

    def validate_response(self, resp):
        """
        Validate that the response is not an error code. If it is, then raise an error
        and display the error message.

        `Args:`
            resp: object
                A response object
        """

        if resp.status_code >= 400:
            if resp.reason:
                message = f"HTTP error occurred ({resp.status_code}): {resp.reason}"
            elif resp.text:
                message = f"HTTP error occurred ({resp.status_code}): {resp.text}"
            else:
                message = f"HTTP error occurred ({resp.status_code})"

            # Some errors return JSONs with useful info about the error. Return it if exists.
            if self.json_check(resp):
                raise HTTPError(f"{message}, json: {resp.json()}")
            else:
                raise HTTPError(message)

    def data_parse(self, resp):
        """
        Determines if the response json has nested data. If it is nested, it just returns the
        data. This is useful in dealing with requests that might return multiple records, while
        others might return only a single record.

        `Args:`
            resp:
                A response dictionary
        `Returns:`
            dict
                A dictionary of data.
        """

        # TODO: Some response jsons are enclosed in a list. Need to deal with unpacking and/or
        # not assuming that it is going to be a dict.

        # In some instances responses are just lists.
        if isinstance(resp, list):
            return resp

        if self.data_key and self.data_key in resp.keys():
            return resp[self.data_key]
        else:
            return resp

    # There are many different ways in which APIs indicate whether there is a next page
    # of data following the initial request. The goal is build out a series of utilities
    # that mean most of the most common use cases.

    def next_page_check_url(self, resp):
        """
        Check to determine if there is a next page. This requires that the response json
        contains a pagination key that is empty if there is not a next page.

        `Args:`
            resp:
                A response dictionary
        `Returns:
            boolean
        """

        if self.pagination_key and self.pagination_key in resp.keys():
            if resp[self.pagination_key]:
                return True
        else:
            return False

    def json_check(self, resp):
        """
        Check to see if a response has a json included in it.
        """

        try:
            resp.json()
            return True
        except JSONDecodeError:
            return False
