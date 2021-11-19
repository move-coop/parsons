from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.oauth_api_connector import OAuthAPIConnector


class Controlshift(object):
    def __init__(self, hostname=None, client_id=None, client_secret=None) -> None:
        self.hostname = check_env.check('CONTROLSHIFT_HOSTNAME', hostname)
        token_url = f'{self.hostname}/oauth/token'
        self.client = OAuthAPIConnector(
            self.hostname,
            client_id=check_env.check('CONTROLSHIFT_CLIENT_ID', client_id),
            client_secret=check_env.check('CONTROLSHIFT_CLIENT_SECRET', client_secret),
            token_url=token_url,
            auto_refresh_url=token_url
        )

    def get_petitions(self):
        next_page = 1
        petitions = []
        while next_page:
            response = self.client.get_request(
                f'{self.hostname}/api/v1/petitions', {'page': next_page})
            next_page = response['meta']['next_page']
            petitions.extend(response['petitions'])

        return Table(petitions)
