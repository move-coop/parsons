from requests import request as _request
import logging

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

        self.uri = uri
        self.headers = headers
        self.auth = auth
        self.pagination_key = pagination_key
        self.data_key = data_key

    def request(self, url, req_type, json=None, data=None, params=None, raise_on_error=True):
        """
        Base request using requests libary.

        `Args:`
            url: str
                The url request string
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

        r = _request(req_type, url, headers=self.headers, auth=self.auth, json=None, data=None,
                     params=params)

        # To Do: Implement better and more robust error handling method, but this
        # will work for the time being.
        if raise_on_error:
            r.raise_for_status()

        return r

    def get_request(self, url, params=None):
        """
        Args:
            url: str
                A complete and valid url for the api request
            params: dict
                The request parameters
        Returns:
                A requests response object
        """

        r = self.request(url, req_type='GET', params=None)
        return r.json()

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

        # To Do: Some response jsons are enclosed in a list. Need to deal with unpacking and/or
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

        # To Do: Some response jsons are enclosed in a list. Need to deal with unpacking and/or
        # not assuming that it is going to be a dict.

        if self.pagination_key and self.pagination_key in resp.keys():
            if resp[self.pagination_key]:
                return True
        else:
            return False
