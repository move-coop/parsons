import logging
from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector


logger = logging.getLogger(__name__)


class Quickbase(object):
    """
    Instantiate the Quickbase class

    `Args:`
        hostname: str
            The URL for the homepage/login page of the organization's Quickbase
            instance (e.g. demo.quickbase.com).
        user_token: str
            The Quickbase account user token (API key). Not required if
            ``QUICKBASE_USER_TOKEN`` env variable is set.
    `Returns:`
        Quickbase Class
    """

    def __init__(self, hostname=None, user_token=None):
        self.hostname = check_env.check("QUICKBASE_HOSTNAME", hostname)
        self.user_token = check_env.check("QUICKBASE_USER_TOKEN", user_token)
        self.api_hostname = "https://api.quickbase.com/v1"
        self.client = APIConnector(
            self.api_hostname,
            headers={
                "QB-Realm-Hostname": self.hostname,
                "AUTHORIZATION": f"QB-USER-TOKEN {self.user_token}",
            },
        )

    def get_app_tables(self, app_id=None):
        """
        Query records in a Quickbase table. This follows the patterns laid out
        in Quickbase query documentaiton, located here:
        https://help.quickbase.com/api-guide/componentsquery.html

        `Args:`
            app_id: str
                Identifies which Quickbase app from which to fetch tables.
        `Returns:`
            Table Class
        """
        return Table(
            self.client.request(f"{self.api_hostname}/tables?appId={app_id}", "GET").json()
        )

    def query_records(self, table_from=None):
        """
        Query records in a Quickbase table. This follows the patterns laid out
        in Quickbase query documentaiton, located here:
        https://help.quickbase.com/api-guide/componentsquery.html

        `Args:`
            from: str
                The ID of a Quickbase resource (i.e. a table) to query.
        `Returns:`
            Table Class
        """
        req_resp = self.client.request(
            f"{self.api_hostname}/records/query", "POST", json={"from": table_from}
        ).json()

        resp_tbl = Table(req_resp["data"])
        cleaned_tbl = Table()

        for row in resp_tbl:
            row_dict = {}
            for column in resp_tbl.columns:
                row_dict[column] = row[column]["value"]
            cleaned_tbl.concat(Table([row_dict]))
            cleaned_tbl.materialize()

        column_resp = req_resp["fields"]
        column_map = {}
        for entry in column_resp:
            column_map[str(entry["id"])] = entry["label"].lower().strip()

        for column in cleaned_tbl.columns:
            cleaned_tbl.rename_column(column, column_map[column])

        return cleaned_tbl
