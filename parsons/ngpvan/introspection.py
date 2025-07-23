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

        response = tuple(self.connection.items("apiKeyProfiles"))
        logger.info(f"Returned {len(response)} API key profiles. Returning the first one.")
        return response[0]
