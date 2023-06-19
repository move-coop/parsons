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

    def get_p2ps(self, **kwargs):
        """
        Sends a GET request to the /p2ps endpoint with specified parameters,
        and returns the response in a Table object.

        The Strive connector uses horizontal filtering. You can learn more about
        horizontal filtering here: https://postgrest.org/en/stable/references/api/tables_views.html#horizontal-filtering-rows

        For example, if you want to filter on a specific `id`, you would pass `eq.12345` to the `id` param
        where `12345` is the P2P id. 

        If you want to search on a key word in a message, you would pass `like*hello*` to the `message` param
        where `hello` is the keyword you want to search for in the message. The `*` is a wildcard operator
        similar to `%` in SQL.


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

        # Build URL
        full_url = self.build_url(kwargs, "p2ps")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table
       
    def get_custom_fields(self, **kwargs):
        """
        Sends a GET request to the /custom_fields endpoint with specified parameters,
        and returns the response in a Table object.

        The Strive connector uses horizontal filtering. You can learn more about
        horizontal filtering here: https://postgrest.org/en/stable/references/api/tables_views.html#horizontal-filtering-rows

        For example, if you want to filter on a specific `campaign_id`, you would pass `eq.12345` to the `campaign_id` param
        where `12345` is the campaign id. 

        `Args:`
            campaign_id: int
                The ID of the campaign that the P2P message is associated with.
            field: str 
                The name of the field within the API
            label: str
                The name of the field within the product
            type: str
                The type of field the custom field is
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
        # Build URL
        full_url = self.build_url(kwargs, "custom_fields")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table
    
    def get_outgoing_messages(self, **kwargs):
        """
        Sends a GET request to the /outgoing_messages endpoint with specified parameters,
        and returns the response in a Table object.

        The Strive connector uses horizontal filtering. You can learn more about
        horizontal filtering here: https://postgrest.org/en/stable/references/api/tables_views.html#horizontal-filtering-rows

        For example, if you want to filter on a specific `campaign_id`, you would pass `eq.12345` to the `campaign_id` param
        where `12345` is the campaign id. 

        `Args:`
            id: string <integer>
                The ID of the outgoing message
            campaign_id: string <integer>
                The campaign associated with the outgoing message
            member_id: string <integer> 
                The member targeted by the outgoing message
            message: string <character varying>
                The contents of the outgoing message
            broadcast_id: string <integer>
                The parent broadcast that the outgoing message was part of
            p2p_id: string <integer>
                The ID of the inbox message the outgoing message was part of
            flow_action_id: string <text>
                The flow action that happened in response to the outgoing message
            status: string <character varying>
                That status of the outgoing message's delivery
            error_code: string <integer>
                The error code returned by carriers in repsonse to the outgoing message
            sent_at: string <timestamp with time zone>
                When the outgoing message was sent
            queued_at: string <text>
                When the outgoing message was added to our aggregators queue
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
        
        # Build URL
        full_url = self.build_url(kwargs, "custom_fields")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table
    
    def get_members(self, **kwargs):
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

        # Build URL 
        full_url = self.build_url(kwargs, "members")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Convert the API response to a Parsons Table object
        table = Table(response)
        return table
        

    def get_broadcasts_groups(self, **kwargs):
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

        # Build URL
        full_url = self.build_url(kwargs, "broadcast_groups")

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

        # Build URL
        full_url = self.build_url(kwargs, "broadcasts")

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