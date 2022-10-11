import logging
import os
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons import Table

logger = logging.getLogger(__name__)


class Strive(object):
    """
    Instantiate Strive class.

    `Args:`
    """

    def __init__(self, api_key=None):
        self.api_key = check_env.check("STRIVE_KEY", api_key)
        self.uri = "https://api.strivedigital.org"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.client = APIConnector(self.uri, headers=self.headers)

    def get_members(self, params: dict):
        response = self.client.get_request(url="members", params=params)
        return Table(response)


# Instrantiate Strive class
s = Strive()

# Headers
data = {"limit": "5"}
# Testing get members
response = s.get_members(params=data)
# Convert data into Parsons Table

print(response.num_rows)

# Put results into Parsons table

## To Do
# Create Other Get Methods 
# Specifying other paramters instead of taking them as a dictionary 
# Tackle POST methods 