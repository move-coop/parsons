from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from parsons.utilities.api_connector import APIConnector
import urllib.parse


class OAuthAPIConnector(APIConnector):
    def __init__(self, uri, headers=None, auth=None, pagination_key=None, data_key=None, client_id=None, client_secret=None, token_url=None):
        super().__init__(uri, headers=headers, auth=auth, pagination_key=pagination_key, data_key=data_key)

        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        self.token = oauth.fetch_token(token_url=token_url,
                                       client_id=client_id, client_secret=client_secret)
        self.client = OAuth2Session(client_id, token=self.token,
                                    auto_refresh_url=token_url, token_updater=self.token_saver)

    def request(self, url, req_type, json=None, data=None, params=None):
        full_url = urllib.parse.urljoin(self.uri, url)
        return self.client.request(req_type, full_url, headers=self.headers, auth=self.auth, json=json, data=data, params=params)

    def token_saver(self, token):
        self.token = token
