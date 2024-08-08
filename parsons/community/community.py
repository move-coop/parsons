import logging
from parsons.utilities.api_connector import APIConnector
from parsons.utilities import check_env
from parsons.etl import Table

logger = logging.getLogger(__name__)

POLLING_DELAY = 1
COMMUNITY_API_ENDPOINT = "https://dl.community.com/download/v1/files/"


class Community(object):
    """
    Instantiate class.

       `Args:`
            community_client_id: str
                The Community provided Client ID. Not required if ``COMMUNITY_CLIENT_ID`` env
                variable set.
            community_access_token: str
                The Community provided access token. Not required if ``COMMUNITY_ACCESS_TOKEN`` env
                variable set.
            community_uri: str
                The URI to access the CSV API. Not required, default is
                https://secure.actblue.com/api/v1. You can set an ``ACTBLUE_URI`` env variable or
                use this URI parameter if a different endpoint is necessary - for example, when
                running this code in a test environment where you don't want to hit the actual API.
    """

    def __init__(self, community_client_id=None, community_access_token=None, community_url=None):
        self.community_client_id = check_env.check("community_client_id", community_client_id)
        self.community_access_token = check_env.check(
            "community_access_token", community_access_token
        )
        self.uri = (
            check_env.check("COMMUNITY_URL", community_url, optional=True)
            or f"{COMMUNITY_API_ENDPOINT}/{community_client_id}/"
        )
        self.headers = {
            "Authorization": f"Bearer {self.community_access_token}",
            # "accept": "*/*",
            # "accept-encoding": "gzip",
        }
        self.client = APIConnector(
            self.uri,
            headers=self.headers,
        )

    def get_request(self, filename):
        """
        GET request to Community.com API to get the CSV data.

        `Args:`
            filename: str
                Data filename you are requesting.
                Options:
                    'campaigns': Campaign Performance data
                    'outbound_message_type_usage`: Message Segment Usage data
                    'campaign_links': Campaign Link Performance data
                    'members': Member Details data
                    'member_state_changes': Member Subscription Status data
                    'custom_member_data': Custom Member Data
                    'communities': Communities data
                    'member_communities': Member Communities data

        `Returns:`
            Response of GET request; a successful response returns the CSV formatted data
        """

        logger.info(f"Requesting {filename}")
        url = (
            f"{filename}.csv.gz"
            if filename != "outbound_message_type_usage"
            else f"{filename}.csv.gz/segment-based-subscription"
        )
        print(f"URL: {url}")
        response = self.client.get_request(url=url, return_format="content")
        return response

    def get_data_export(self, filename):
        """
        Get specified data from Community.com API as Parsons table.

        `Args:`
            filename: str
                Data filename you are requesting.
                Options:
                    'campaigns': Campaign Performance data
                    'outbound_message_type_usage`: Message Segment Usage data
                    'campaign_links': Campaign Link Performance data
                    'members': Member Details data
                    'member_state_changes': Member Subscription Status data
                    'custom_member_data': Custom Member Data
                    'communities': Communities data
                    'member_communities': Member Communities data

        `Returns:`
            Contents of the generated contribution CSV as a Parsons table.
        """

        get_request_response = self.get_request(filename=filename)
        response_string = get_request_response.decode("utf-8")
        table = Table.from_csv_string(response_string)
        return table