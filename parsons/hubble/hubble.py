import logging
from parsons.hubble.hubble_connector import HubbleConnector
from parsons.hubble.ping import Ping

logger = logging.getLogger(__name__)

class Hubble(Ping):
    """
    Returns the Hubble class.
    For instructions on how to generate a Access Credentials visit https://docs.hubble.vote/.

    `Args:`
        hubble_api_username : str
            A valid api username. Not required if ``HUBBLE_API_USERNAME`` env variable set.
        hubble_api_password: str
            A valid api username. Not required if ``HUBBLE_API_PASSWORD`` env variable set.
        uri: str
            Base uri to make api calls.
    `Returns:`
        Hubble object
    """
    def __init__(self, hubble_api_username=None, hubble_api_password=None, uri=None):
        self.connection = HubbleConnector(username=hubble_api_username, password=hubble_api_password)
