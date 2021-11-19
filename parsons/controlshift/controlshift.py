from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.oauth_api_connector import OAuthAPIConnector


class Controlshift(object):
    def __init__(self, hostname=None, client_id=None, client_secret=None) -> None:
        self.hostname = check_env.check('CONTROLSHIFT_HOSTNAME', hostname)
        self.client = OAuthAPIConnector(
            self.hostname,
            client_id=check_env.check('CONTROLSHIFT_CLIENT_ID', client_id),
            client_secret=check_env.check('CONTROLSHIFT_CLIENT_SECRET', client_secret),
            token_url=f'{self.hostname}/oauth/token'
        )

    def get_petitions(self):
        response = self.client.request(
            f'{self.hostname}/api/v1/petitions?page=1', 'GET').json()
        return Table(response['petitions'])
