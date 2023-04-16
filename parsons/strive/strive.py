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


    def get_members(self, **kwargs):
        """
        The get_members method sends a GET request to the /members endpoint with specified parameters, and returns the response in a Table object.

        `Args:`
            id: str <integer>
                Filter to the ID of the member
            campaign_id: str <integer>
                Filter to members associated with a specific `campaign_id`.
            phone_number: str
                Filter to members associated with the specified phone number.
             only sent on the specified date (ex. ``2019-01-01``).
            first_name: str
                Filter to the first name of the member.
            last_name: str
                Filter to the last name of the member.
            city: str
                Filter to the city of the member.
            state: str
                Filter to the state of the member.
            postal_code: str
                Filter to the postal code of the member.
            email: str
                Filter to the email address of the member.
            notes: str
                Filter to the content of notes associated with the member
            additional_notes: str
                Filter to the content of additional notes field associated with the member
            opt_in: str
                Filter on whether or not the member is subscribed to recieve further messages
            custom: str
                Filter on the  custom fields associated with the member
            created_at: str
                Filter on  the member was either first imported or opted-in to recieve messages
            updated_at: str
                Filter on when the member was last updated with a change
            groups: str
                Filter on the groups the member belongs to 
            carrier: str
                Filter on the mobile carrier of the user
            first_sub_id: str
                Filter on the ID of the first subscription event retained for the member.
            select: str
                Select for specific columns to be returned
            order: str
                Order the results returned.
            offset: str
                Offset the results returned.
            limit: str
                Limit the results returned.
        `Raises:`
            ValueError: If an invalid parameter is passed or if a parameter's value does not match the expected data type.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
    
        valid_params = {
            "id": str,
            "campaign_id": str,
            "phone_number": str,
            "first_name": str,
            "last_name": str,
            "city": str,
            "state": str,
            "postal_code":str,
            "email":str,
            "notes":str,
            "additional_notes":str,
            "opt_in":str,
            "custom":str,
            "created_at":str,
            "updated_at":str,
            "groups":str,
            "carrier":str,
            "first_sub_id":str,
            "select": str,
            "order":str,
            "offset":str,
            "limit":str
        }

        # Check that params are in list of valid paramaters
        invalid_params = [k for k in kwargs if k not in valid_params]
        if invalid_params:
            raise ValueError(f"Invalid parameter(s) passed: {', '.join(invalid_params)}")

        # Check that params match the correct data type
        for key, value in kwargs.items():
            if key in valid_params:
                if not isinstance(value, valid_params[key]):
                    raise ValueError(f"Invalid data type for parameter '{key}': expected {valid_params[key]}, got {type(value)}")
                if value is not None:
                    params[key] = value
        
        # Make the get request at the /members endpoint
        response = self.client.get_request(url="members", params=params)
        return Table(response)

    def get_broadcasts(self, params: dict):
        response = self.client.get_request(url="broadcasts", params=params)
        return Table(response) 

    def get_p2ps(self, params: list):
        response = self.client.get_request(url="p2ps", params=params)
        return Table(response)
    
    def get_custom_fields(self, params: dict):
        response = self.client.get_request(url="custom_fields", params=params)
        return Table(response)

## To Do
# Create Other Get Methods 
# Specifying other paramters instead of taking them as a dictionary 
# Tackle POST methods 