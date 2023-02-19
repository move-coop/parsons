"""Hubble Ping Endpoints"""

import uuid
import logging
import petl

logger = logging.getLogger(__name__)

class Ping(object):

    def __init__(self, hubble_connection):
        self.connection = hubble_connection

    def get_ping(self):
        """
        GET request to retrieve download_url for generated CSV.

        `Returns:`
            While CSV is being generated, 'None' is returned. When CSV is ready, the method returns
            the download_url.
        """
        return self.client.get_request(url="ping")