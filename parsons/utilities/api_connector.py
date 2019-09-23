from requests import request as _request
import logging

logger = logging.getLogger(__name__)


class APIConnector(object):
    """
    The API Connector is a low level class for API requests that other connectors
    can utilize.

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

        if raise_on_error:
            r.raise_for_status()

        return r

    def base_get_request(self, url, params=None, raise_on_error=True):
        """
        Args:
            url: str
                A complete and valid url for the api request
            headers: dict
                The header dict
            auth: dict
                The authentication dict
            params: dict
                The request parameters
            raise_on_error: bool
                Raise if status code returns an error
        Returns:
                A requests response object
        """

        r = self.request(url, req_type='GET', params=None)

        # To Do: Implement better and more robust error handling method, but this
        # will work for the time being.
        if raise_on_error:
            r.raise_for_status()

        return r.json()

    def get_request(self, endpoint, **kwargs):
        """
        Get request including pagination.

        `Args:`
            endpoint: str
                The api endpoint. Add to the end of the uri to create a complete and
                valid url.
            **kwargs: args
                Kwargs for the :meth:`APIConnector.base_get_request`
        """

        url = self.uri + endpoint

        r = self.base_get_request(endpoint, **kwargs)

        data = self.data_parse(r)

        # Paginate
        while self.next_page_check(r):
            url = self.pagination_key
            r = self.base_get_request(url, **kwargs)
            data.extend(r.json[self.data_key])

        return data

    def next_page_check(self, resp):
        """
        Check to determine if there is a next page.
        """

        if self.pagination_key and self.pagination_key in resp.keys():
            if resp[self.pagination_key]:
                return True
        else:
            return False

    def data_parse(self, resp):
        """
        Determines if the response json has nested data. If it is nested, it just returns the
        data. This is useful in dealing with requests that might return multiple records, while
        others might return only a single record.
        """

        # To Do: Some response jsons are enclosed in a list. Need to deal with unpacking and/or
        # not assuming that it is going to be a dict.

        if self.data_key and self.data_key in resp.keys():
            return resp[self.data_key]
        else:
            return resp
