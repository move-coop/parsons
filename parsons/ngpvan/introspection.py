import logging

logger = logging.getLogger(__name__)


class Introspection:
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_apikeyprofiles(self):
        """
        Get API key profiles.

        Args:
            None
        Returns:
            JSON response

        """

        response = self.connection.get_request("apiKeyProfiles")
        logger.info(f"Returned {len(response[0])} API key profiles.")
        return response[0]
