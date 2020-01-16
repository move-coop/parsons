from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons import Table
import logging
import jwt
import datetime
import json

logger = logging.getLogger(__name__)

ZOOM_URI = 'https://api.zoom.us/v2/'

# To Do:
# - Add unittests
# - Add to docs


class Zoom():
    """
    Instantiate the Zoom class.

    `Args:`
        api_key: str
            A valid Zoom api key. Not required if ``ZOOM_API_KEY`` env
            variable set.
        api_secret:
            A valid Zoom api secret. Not required if ``ZOOM_API_SECRET`` env
            variable set.
    """

    def __init__(self, api_key=None, api_secret=None):

        self.api_key = check_env.check('ZOOM_API_KEY', api_key)
        self.api_secret = check_env.check('ZOOM_API_SECRET', api_secret)
        self.client = APIConnector(ZOOM_URI)

    def refresh_header_token(self):
        # Generate a token that is valid for 30 seconds and update header

        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"iss": self.api_key, "exp": int(datetime.datetime.now().timestamp() + 30)}
        token = jwt.encode(payload, self.api_secret, algorithm='HS256').decode("utf-8")
        self.client.headers = {'authorization': f"Bearer {token}", 'content-type': "application/json"}

    def get_request(self, endpoint, data_key):
        # Internal Get request method.

        self.refresh_header_token()
        r = self.client.get_request(endpoint)
        self.client.data_key = data_key
        data = self.client.data_parse(r)

        # Paginate
        while r['page_number'] < r['page_count']:
            r = self.client.get_request(endpoint)
            data = self.api.data_parse(r)

        return Table(data)

    def get_users(self, status):
        """
        Get users.

        `Args:`
            status: str
                One of the following: active, inactive, pending. Defaults to active.

        `Returns:`
            A parsons Table.
        """

        tbl = self.get_request('users', 'users', status=status)
        logger.info(f'Retrieved {tbl.num_rows} users.')

        # To Do:
        # Melissa needs to test this
        # Add optional argument of role_id
        
        pass

    def get_webinars(self, user_id):
        """
        Get webinars.

        `Args:`
            user_id: str
                A user id
        `Returns:`
            A parsons Table.
        """

        tbl = self.get_request(f'users/{user_id}/webinars', 'webinars')
        logger.info(f'Retrieved {tbl.num_rows} webinars.')
        return tbl

    def get_webinar_participants(self):

        # To do...
        pass
