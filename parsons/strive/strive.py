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


    def get_members(self, id=None, campaign_id=None, phone_number=None, sent_on=None,
                    first_name=None, last_name=None, city=None, state=None, postal_code=None,
                    email=None, notes=None, additional_notes=None, opt_in=None, custom=None,
                    created_at=None, updated_at=None, groups=None, carrier=None, first_sub_id=None,
                    select=None, order=None, offset=None, limit=None):
        """
        Sends a GET request to the /members endpoint with specified parameters,
        and returns the response in a Table object.
        """

        params = {}

        # Build dictionary of params
        if id:
            params["id"] = id
        if campaign_id:
            params["campaign_id"] = campaign_id
        if phone_number:
            params["phone_number"] = phone_number
        if sent_on:
            params["sent_on"] = sent_on
        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name
        if city:
            params["city"] = city
        if state:
            params["state"] = state
        if postal_code:
            params["postal_code"] = postal_code
        if email:
            params["email"] = email
        if notes:
            params["notes"] = notes
        if additional_notes:
            params["additional_notes"] = additional_notes
        if opt_in:
            params["opt_in"] = opt_in
        if custom:
            params["custom"] = custom
        if created_at:
            params["created_at"] = created_at
        if updated_at:
            params["updated_at"] = updated_at
        if groups:
            params["groups"] = groups
        if carrier:
            params["carrier"] = carrier
        if first_sub_id:
            params["first_sub_id"] = first_sub_id
        if select:
            params["select"] = select
        if order:
            params["order"] = order
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit


        # Define valid filter parameters and their expected data types
        filter_params = {
            'id': int,
            'campaign_id': int,
            'phone_number': str,
            'sent_on': str,
            'first_name': str,
            'last_name': str,
            'city': str,
            'state': str,
            'postal_code': str,
            'email': str,
            'notes': str,
            'additional_notes': str,
            'opt_in': str,
            'custom': str,
            'created_at': str,
            'updated_at': str,
            'groups': str,
            'carrier': str,
            'first_sub_id': str,
            'select': str,
            'order': str,
            'offset': str,
            'limit': str
        }

        # Validate filter parameters
        for param, value in params.items():
            print(param)
            print(value)
            if param in filter_params:
                expected_type = filter_params[param]
                if not isinstance(value, expected_type):
                    raise ValueError(f"Invalid data type for parameter {param}: expected {expected_type.__name__}")

        # Build the API request URL with filter parameters
        params = {}
        for param, value in params.items():
            if param in filter_params and value is not None:
                params[param] = value

        # Build the query string for the URL
        query_string = '&'.join([f'{key}={value}' for key, value in params.items()])

        # Build the full URL with the query string
        url = "members"
        full_url = f'{url}?{query_string}'

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        if response.status_code == 200:
            # Convert the API response to a Parsons Table object
            table = Table(response)
            if select:
                table = table.select(select)
            if order:
                table = table.order_by(order)
            if offset:
                table = table.offset(offset)
            if limit:
                table = table.limit(limit)
            return table
        else:
            logger.info(f'Error: {response.status_code}')

    def get_broadcasts(self, broadcast_id=None, group_id=None, updated_at=None, campaign_id=None,
                       select=None, order=None, offset=None, limit=None):
        """
        Sends a GET request to the /members endpoint with specified parameters,
        and returns the response in a Table object.
        """

        params = {}

        # Build dictionary of params
        if broadcast_id:
            params["broadcast_id"] = broadcast_id
        if group_id:
            params["group_id"] = group_id
        if updated_at:
            params["updated_at"] = updated_at
        if campaign_id:
            params["campaign_id"] = campaign_id
        if select:
            params["select"] = select
        if order:
            params["order"] = order
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit


        # Define valid filter parameters and their expected data types
        filter_params = {
            'broadcast_id': int,
            'group_id': int,
            'updated_at': str,
            'campaign_id': str,
            'select': str,
            'order': str,
            'offset': str,
            'limit': str
        }

        # Validate filter parameters
        for param, value in params.items():
            print(param)
            print(value)
            if param in filter_params:
                expected_type = filter_params[param]
                if not isinstance(value, expected_type):
                    raise ValueError(f"Invalid data type for parameter {param}: expected {expected_type.__name__}")
 
        # Build the API request URL with filter parameters
        params = {}
        for param, value in params.items():
            if param in filter_params and value is not None:
                params[param] = value

        # Build the query string for the URL
        query_string = '&'.join([f'{key}={value}' for key, value in params.items()])

        # Build the full URL with the query string
        url = "broadcasts_groups"
        full_url = f'{url}?{query_string}'

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        if response.status_code == 200:
            table = Table(response)
            # Convert the API response to a Parsons Table object
            table = Table(response)
            if select:
                table = table.select(select)
            if order:
                table = table.order_by(order)
            if offset:
                table = table.offset(offset)
            if limit:
                table = table.limit(limit)
            return table
        else:
            logger.info(f'Error: {response.status_code}')

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