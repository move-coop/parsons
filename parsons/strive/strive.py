import logging
import os
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons import Table

logger = logging.getLogger(__name__)


class Strive(object):
    """
    Instantiate Strive class.
    """

    def __init__(self, api_key=None):
        self.api_key = check_env.check("STRIVE_KEY", api_key)
        self.uri = "https://api.strivedigital.org"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.client = APIConnector(self.uri, headers=self.headers)

    def validate_filter_params(self, params, filter_params):
        """
        For a given set of params and set paramter types, validate that the
        input params match the set parameter data types.

        Raises an error if an invalid data type has been passed as a parameter.
        """
        # Validate filter parameters
        for param, value in params.items():
            if param in filter_params:
                expected_type = filter_params[param]
                if not isinstance(value, expected_type):
                    raise ValueError(
                        f"Invalid data type for parameter {param}: expected {expected_type.__name__}"
                    )

    def build_url(self, params, endpoint):
        """
        Takes a set of parameters and an API endpoint and builds a URL using horizontal
        filter rules.
        """
        # Build the query string for the URL
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])

        # Build the full URL with the query string
        url = endpoint
        full_url = f"{url}?{query_string}"

        return full_url

    def get_p2ps(
        self,
        id=None,
        user_id=None,
        campaign_id=None,
        message=None,
        attachment=None,
        scheduled_at=None,
        cancelled_at=None,
        sent_at=None,
        created_at=None,
        updated_at=None,
        select=None,
        order=None,
        offset=None,
        limit=None,
    ):
        """
        Sends a GET request to the /p2ps endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: int
                The ID of the P2P message.
            user_id: int
                The ID of the user who created the P2P message.
            campaign_id: int
                The ID of the campaign that the P2P message is associated with.
            message: str
                The text content of the P2P message.
            attachment: str
                A URL to an attachment that was sent with the P2P message.
            scheduled_at: str
                The date and time that the P2P message is scheduled to be sent.
            cancelled_at: str
                The date and time that the P2P message was cancelled, if applicable.
            sent_at: str
                The date and time that the P2P message was sent, if applicable.
            created_at: str
                The date and time that the P2P message was created.
            updated_at: str
                The date and time that the P2P message was last updated.
            select: str
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: str
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: int
                The number of records to skip before returning results.
            limit: int
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /p2ps endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.

        """

        params = {}

        # Build dictionary of params
        if id:
            params["id"] = id
        if user_id:
            params["user_id"] = user_id
        if campaign_id:
            params["campaign_id"] = campaign_id
        if message:
            params["message"] = message
        if attachment:
            params["attachment"] = attachment
        if scheduled_at:
            params["scheduled_at"] = scheduled_at
        if cancelled_at:
            params["cancelled_at"] = cancelled_at
        if sent_at:
            params["sent_at"] = sent_at
        if created_at:
            params["created_at"] = created_at
        if updated_at:
            params["updated_at"] = updated_at
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
            "id": int,
            "campaign_id": int,
            "phone_number": str,
            "sent_on": str,
            "first_name": str,
            "last_name": str,
            "city": str,
            "state": str,
            "postal_code": str,
            "email": str,
            "notes": str,
            "additional_notes": str,
            "opt_in": str,
            "custom": str,
            "created_at": str,
            "updated_at": str,
            "groups": str,
            "carrier": str,
            "first_sub_id": str,
            "select": str,
            "order": str,
            "offset": str,
            "limit": str,
        }

        # Type check params
        self.validate_filter_params(params, filter_params)

        # Build URL
        full_url = self.build_url(params, "p2ps")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table
       
    def get_members(
        self,
        id=None,
        campaign_id=None,
        phone_number=None,
        sent_on=None,
        first_name=None,
        last_name=None,
        city=None,
        state=None,
        postal_code=None,
        email=None,
        notes=None,
        additional_notes=None,
        opt_in=None,
        custom=None,
        created_at=None,
        updated_at=None,
        groups=None,
        carrier=None,
        first_sub_id=None,
        select=None,
        order=None,
        offset=None,
        limit=None,
    ):
        """
        Sends a GET request to the /members endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: int
                The ID of the member
            campaign_id: int
                The campaign associated with the member
            phone_number: str
                The member's phone number
            first_name: str
                The member's first name
            last_name: str
                The member's last name
            city: str
                The City associated with the member
            state: str
                The State assoicated with the member
            postal_code: str
                The zip or postcal code assoicated with the member
            email: str
                The member's email address
            notes: str
                The content of notes associated with the member
            additional_notes: str
                The content of additional notes field associated with the member
            opt_in: str
                Whether or not the member is subscribed to recieve further messages
            custom: str
                The custom fields associated with the member
            created_at: str
                When the member was either first imported or opted-in to recieve messages
            updated_at: str
                When the member was last updated with a change
            group: str
                Groups this member belongs to (json)
            carrier: str
                The mobile carrier this member uses
            first_sub_id: int
                The ID of the first subscription event retained for the member
            select: str
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: str
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: int
                The number of records to skip before returning results.
            limit: int
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /p2ps endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.

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
            "id": int,
            "campaign_id": int,
            "phone_number": str,
            "sent_on": str,
            "first_name": str,
            "last_name": str,
            "city": str,
            "state": str,
            "postal_code": str,
            "email": str,
            "notes": str,
            "additional_notes": str,
            "opt_in": str,
            "custom": str,
            "created_at": str,
            "updated_at": str,
            "groups": str,
            "carrier": str,
            "first_sub_id": str,
            "select": str,
            "order": str,
            "offset": str,
            "limit": str,
        }

        # Type check params 
        self.validate_filter_params(params, filter_params)

        # Build URL 
        full_url = self.build_url(params, "members")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Convert the API response to a Parsons Table object
        table = Table(response)
        return table
        

    def get_broadcasts_groups(
        self,
        broadcast_id=None,
        group_id=None,
        updated_at=None,
        campaign_id=None,
        select=None,
        order=None,
        offset=None,
        limit=None,
    ):
        """
        Sends a GET request to the /broadcasts endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            broadcast_id: int
                The ID of the Broadcast
            group_id: int 
                The ID of the group of members targeted by the broadcast
            updated_at: str
                string <timestamp with time zone>
            campaign_id: int
                The campaign that the broadcast belongs to
            select: str
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: str
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: int
                The number of records to skip before returning results.
            limit: int
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /broadcasts_groups endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
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
            "broadcast_id": int,
            "group_id": int,
            "updated_at": str,
            "campaign_id": str,
            "select": str,
            "order": str,
            "offset": str,
            "limit": str,
        }

        # Type check params
        self.validate_filter_params(params, filter_params)

        # Build URL
        full_url = self.build_url(params, "broadcast_groups")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Convert the API response to a Parsons Table object
        table = Table(response)
        return table

    def get_broadcasts():
        """
        Sends a GET request to the /broadcasts endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: int
                The ID of the Broadcast
            user_id: int 
                The Strive user who sent the broadcast
            campaign_id: int
                The campaign that the broadcast belongs to
            flow_id: int
                The flow that was broadcasted
            name: str
                The name of the Broadcast
            message: str
                The content of the first message sent in the broadcast
            attachment: str
                The attachment or MMS included in the broadcast
            recipient_count: int 
                How many members were targeted for the broadcast
            scheduled_at: str
                When the broadcast is scheduled to send
            cancelled_at: str
                When the broadcast was cancelled
            sent_at: str
                When the broadcast began to deliver
            created_at: str
                When the broadcast was first created
            updated_at: str
                When the broadcast was last updated
            select: str
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: str
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: int
                The number of records to skip before returning results.
            limit: int
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /broadcasts endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """
        params = {}

        # Build dictionary of params
        if id:
            params["id"] = id
        if user_id:
            params["user_id"] = user_id
        if campaign_id:
            params["campaign_id"] = campaign_id
        if flow_id:
            params["flow_id"] = flow_id
        if name:
            params["name"] = name
        if message:
            params["message"] = message
        if attachment:
            params["attachment"] = attachment
        if recipient_count:
            params["recipient_count"] = recipient_count
        if scheduled_at:
            params["scheduled_at"] = scheduled_at
        if cancelled_at:
            params["cancelled_at"] = cancelled_at
        if sent_at:
            params["sent_at"] = sent_at
        if created_at:
            params["created_at"] = created_at
        if updated_at:
            params["updated_at"] = updated_at
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
            "id": int,
            "user_id": int,
            "campaign_id": int,
            "flow_id": int,
            "name": str,
            "message": str,
            "attachment": str,
            "recipient_count": int,
            "scheduled_at": str,
            "cancelled_at": str,
            "sent_at": str,
            "created_at": str,
            "updated_at": str,
            "select": str,
            "order": str,
            "offset": str,
            "limit": str
        }
        
        # Type check params
        self.validate_filter_params(params, filter_params)

        # Build URL
        full_url = self.build_url(params, "broadcasts")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table

# Testing
# strive = Strive()
# strive.get_members(first_name = 'eq.brittany')

#in the docs, youw ant to pass params like this, here is an example. 
# then add link to their documentation 