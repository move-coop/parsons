from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.oauth_api_connector import OAuth2APIConnector


class Controlshift(object):
    """
    Instantiate the Controlshift class. Requires an API Application integration.
    For more info on setup, see:
    https://developers.controlshiftlabs.com/#authenticated-rest-api-quickstart-guide

    `Args:`
        hostname: str
            The URL for the homepage/login page of the organization's Controlshift
            instance (e.g. https://demo.controlshift.app). Not required if
            ``CONTROLSHIFT_HOSTNAME`` env variable is set.
        client_id: str
            The Client ID for your REST API Application. Not required if
            ``CONTROLSHIFT_CLIENT_ID`` env variable is set.
        client_secret: str
            The Client Secret for your REST API Application. Not required if
            ``CONTROLSHIFT_CLIENT_SECRET`` env variable is set.
    `Returns:`
        Controlshift Class
    """

    def __init__(self, hostname=None, client_id=None, client_secret=None):

        self.hostname = check_env.check("CONTROLSHIFT_HOSTNAME", hostname)

        # Hostname must start with 'https://'
        if self.hostname.startswith("http://"):
            self.hostname = self.hostname.replace("http://", "https://")
        if not self.hostname.startswith("https://"):
            self.hostname = "https://" + self.hostname

        token_url = f"{self.hostname}/oauth/token"
        self.client = OAuth2APIConnector(
            self.hostname,
            client_id=check_env.check("CONTROLSHIFT_CLIENT_ID", client_id),
            client_secret=check_env.check("CONTROLSHIFT_CLIENT_SECRET", client_secret),
            token_url=token_url,
            auto_refresh_url=token_url,
        )

    def get_petitions(self) -> Table:
        """
        Get a full list of all petitions, including ones that are unlaunched or otherwise not
        visible to the public.

        `Return:`
            Table Class
        """
        next_page = 1
        petitions = []
        while next_page:
            response = self.client.get_request(
                f"{self.hostname}/api/v1/petitions", {"page": next_page}
            )
            next_page = response["meta"]["next_page"]
            petitions.extend(response["petitions"])

        return Table(petitions)

        def get_signatures(self):
            pass

        def get_members(self):
            pass

        def get_partnerships(self):
            pass

        def get_events(self):
            pass

        def get_attendees(self):
            pass

        def get_calendars(self):
            pass

        def get_local_groups(self):
            pass
