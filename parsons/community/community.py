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
            "Aurthorization": f"Bearer {self.community_access_token}",
            "accept": "application/json",
        }
        self.client = APIConnector(
            self.uri,
            headers=self.headers,
        )

    def get_request(self, resource, data_type="csv"):
        """
        GET request to Community.com API to get the CSV/JSON data.

        `Args:`
            data_type: str
                Type of data you are requesting, CSV or JSON
            resource: str
                Data resource you are requesting.
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
            Response of POST request; a successful response includes 'body', the actual CSV or JSON formatted data
        """

        logger.info(f"Requesting {resource} as {data_type}.")
        url = (
            f"{resource}.{data_type}.gz"
            if resource != "outbound_message_type_usage"
            else f"{resource}.{data_type}.gz/segment-based-subscription"
        )
        response = self.client.get_request(url=url)
        return response

    def get_resource(self, resource, data_type="csv"):
        """
        Get specified data from Community.com API as Parsons table.

        `Args:`
            data_type: str
                Type of data you are requesting, CSV or JSON
            resource: str
                Data resource you are requesting.
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

        post_request_response = self.get_request(resource=resource, data_type=data_type)
        content = post_request_response["body"]
        table = Table.from_csv(content)
        logger.info("Completed conversion to Parsons Table.")
        return table
