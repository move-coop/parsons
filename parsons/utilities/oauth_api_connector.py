import urllib.parse
from typing import Dict, Optional

from oauthlib.oauth2 import BackendApplicationClient
from parsons.utilities.api_connector import APIConnector
from requests_oauthlib import OAuth2Session


class OAuth2APIConnector(APIConnector):
    """
    The OAuth2API Connector is a low level class for authenticated API requests using OAuth2.
    It extends APIConnector by wrapping the request methods in a server-side OAuth2 client
    and otherwise provides the same interface as APIConnector.

    `Args:`
        uri: str
            The base uri for the api. Must include a trailing '/' (e.g. ``http://myapi.com/v1/``)
        client_id: str
            The client id for acquiring and exchanging tokens from the OAuth2 application
        client_secret: str
            The client secret for acquiring and exchanging tokens  from the OAuth2 application
        token_url: str
            The URL for acquiring new tokens from the OAuth2 Application
        auto_refresh_url: str
            If provided, the URL for refreshing tokens from the OAuth2 Application
        headers: dict
            The request headers
        pagination_key: str
            The name of the key in the response json where the pagination url is
            located. Required for pagination.
        data_key: str
            The name of the key in the response json where the data is contained. Required
            if the data is nested in the response json
    `Returns`:
        OAuthAPIConnector class
    """

    def __init__(
        self,
        uri: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        auto_refresh_url: Optional[str],
        headers: Optional[Dict[str, str]] = None,
        pagination_key: Optional[str] = None,
        data_key: Optional[str] = None,
        grant_type: str = "client_credentials",
        authorization_kwargs: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            uri,
            headers=headers,
            pagination_key=pagination_key,
            data_key=data_key,
        )

        if not authorization_kwargs:
            authorization_kwargs = {}

        client = BackendApplicationClient(client_id=client_id)
        client.grant_type = grant_type
        oauth = OAuth2Session(client=client)
        self.token = oauth.fetch_token(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
            **authorization_kwargs,
        )
        self.client = OAuth2Session(
            client_id,
            token=self.token,
            auto_refresh_url=auto_refresh_url,
            token_updater=self.token_saver,
            auto_refresh_kwargs=authorization_kwargs,
        )

    def request(self, url, req_type, json=None, data=None, params=None):
        """
        Base request using requests libary.

        `Args:`
            url: str
                The url request string; if ``url`` is a relative URL, it will be joined with
                the ``uri`` of the ``OAuthAPIConnector`; if ``url`` is an absolute URL, it will
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

        `Returns:`
            requests response
        """
        full_url = urllib.parse.urljoin(self.uri, url)
        return self.client.request(
            req_type,
            full_url,
            headers=self.headers,
            auth=self.auth,
            json=json,
            data=data,
            params=params,
        )

    def token_saver(self, token):
        self.token = token
