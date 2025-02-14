import logging

logger = logging.getLogger(__name__)


class Introspection(object):
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_apikeyprofiles(self):
        """
        Get API key profiles.

        `Args:`
            None
        `Returns:`
            JSON response
        """

        response = self.connection.get_request("apiKeyProfiles")
        return response[0]
