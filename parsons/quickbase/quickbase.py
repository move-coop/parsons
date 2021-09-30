from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector


class Quickbase(object):
    """
    Instantiate the Quickbase class

    `Args:`
        hostname: str
            The URL for the homepage/login page of the organization's Quickbase instance (e.g. demo.quickbase.com).
        user_token: str
            The Quickbase account user token (API key). Not required if ``QUICKBASE_USER_TOKEN`` env variable
            set.
    `Returns:`
        Quickbase Class
    """
    def __init__(self, hostname=None, user_token=None):
        self.hostname = check_env.check('QUICKBASE_HOSTNAME', hostname)
        self.user_token = check_env.check('QUICKBASE_USER_TOKEN', user_token)
        self.client = APIConnector('https://api.quickbase.com/v1/',
                                   headers={'QB-Realm-Hostname': self.hostname,
                                            'AUTHORIZATION': 'QB-USER-TOKEN ' + self.user_token})

    def list_app_tables(self, app_id=None):
        """
        Get metadata about tables in a QuickBase app.

        `Args:`
            app_id: str
                Identifies which Quickbase app from which to fetch tables.
        `Returns:`
            Table Class
        """
        return Table(self.client.request(f'https://api.quickbase.com/v1/tables?appId={app_id}',
                                         'GET').json())

    def query_records(self, table_from=None):
        """
        Query records in a Quickbase table.

        `Args:`
            from: str
                The ID of a Quickbase resource (i.e. a table) to query.
        `Returns:`
            Table Class
        """
        return Table(self.client.request(f'https://api.quickbase.com/v1/records/query',
                                         'POST', json={"from": table_from}).json())
