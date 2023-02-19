from suds.client import Client
import logging
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

API_ENDPOINT = "https://api.hubble.vote"

class HubbleConnector(object):

    def __init__(self, username=None, password=None, uri=None):
        self.hubble_api_username = check_env.check('HUBBLE_API_USERNAME', hubble_api_username)
        self.hubble_api_password = check_env.check('HUBBLE_API_PASSWORD', hubble_api_password)
        self.uri = check_env.check('HUBBLE_URI', hubble_uri, optional=True) or API_ENDPOINT
        self.headers = {
            "accept": "application/json",
        }
        self.client = APIConnector(self.uri,
                                   auth=(self.hubble_api_username, self.hubble_api_password),
                                   headers=self.headers)

    def get_request(self, endpoint, **kwargs):

        r = self.api.get_request(self.uri + endpoint, **kwargs)
        data = self.api.data_parse(r)

        # Paginate
        while isinstance(r, dict) and self.api.next_page_check_url(r):
            if endpoint == 'savedLists' and not r['items']:
                break
            if endpoint == 'printedLists' and not r['items']:
                break
            r = self.api.get_request(r[self.pagination_key], **kwargs)
            data.extend(self.api.data_parse(r))
        return data

    def post_request(self, endpoint, **kwargs):

        return self.api.post_request(endpoint, **kwargs)

    def delete_request(self, endpoint, **kwargs):

        return self.api.delete_request(endpoint, **kwargs)

    def patch_request(self, endpoint, **kwargs):

        return self.api.patch_request(endpoint, **kwargs)

    def put_request(self, endpoint, **kwargs):

        return self.api.put_request(endpoint, **kwargs)
