import urllib.parse
from typing import Any, Literal

from oauthlib.oauth2 import BackendApplicationClient, OAuth2Token
from requests import Response
from requests_oauthlib import OAuth2Session

from parsons.utilities.api_connector import APIConnector


class OAuth2APIConnector(APIConnector):
    """
    Low level class for authenticated API requests using OAuth2 that other connectors can utilize.

    It extends APIConnector by wrapping the request methods in a server-side OAuth2 client.
    Otherwise, it provides the same interface as APIConnector.

    """

    def __init__(
        self,
        uri: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        auto_refresh_url: str | None,
        headers: dict[str, str] | None = None,
        pagination_key: str | None = None,
        data_key: str | None = None,
        grant_type: str = "client_credentials",
        authorization_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the APIConnector.

        Args:
            uri:
                The base uri for the api.
                Must include a trailing '/' (e.g. ``http://myapi.com/v1/``)
            client_id: The client id for acquiring and exchanging tokens from the OAuth2 application
            client_secret: The client secret for acquiring and exchanging tokens from the OAuth2 application
            token_url: The URL for acquiring new tokens from the OAuth2 Application
            auto_refresh_url: If provided, the URL for refreshing tokens from the OAuth2 Application
            headers: The request headers
            pagination_key:
                The name of the key in the response json where the pagination url is located.
                Required for pagination.
            data_key:
                The name of the key in the response json where the data is contained.
                Required if the data is nested in the response json

        """
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

    def request(
        self,
        url: str,
        req_type: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        *,
        json: dict | None = None,
        data: str | bytes | dict | list[tuple] | None = None,
        params: dict | None = None,
        raise_on_error: bool = True,
        **kwargs,
    ) -> Response:
        """
        Base request using requests libary.

        Args:
            url: str
                The url request string.
                If ``url`` is a relative URL, it will be joined with the ``uri`` of the ``OAuthAPIConnector`.
                if ``url`` is an absolute URL, it will be used as is.
            req_type: str
                The request type.
                One of ``GET``, ``POST``, ``PUT``, ``PATCH``, ``DELETE``, or ``OPTIONS``.
            json:
                The payload of the request object.
                By using `json`, it will automatically serialize the dictionary
            data:
                The payload of the request object.
                Used instead of `json` in some instances.
            params: The parameters to append to the url (e.g. http://myapi.com/things?id=1)
            raise_on_error:
                If the request yields an error status code (anything above 400),
                raise an error. In most cases, this should be ``True``,
                however in some cases, if you are looping through data,
                you might want to ignore individual failures.
            `**kwargs`:
                Additional keyword arguments to pass to :func:`requests.request`.

        """
        full_url = urllib.parse.urljoin(self.uri, url)

        resp = self.client.request(
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

    def token_saver(self, token: OAuth2Token) -> None:
        """Replace the token in the class instance."""
        self.token = token
