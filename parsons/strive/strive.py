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
        full_url = self.build_url(kwargs, "outgoing_messages")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table

    def get_subscription_events(self, **kwargs):
        """
        Sends a GET request to the /subscription_events endpoint with specified parameters,
        and returns the response in a Table object.

        The Strive connector uses horizontal filtering. You can learn more about
        horizontal filtering here: https://postgrest.org/en/stable/references/api/tables_views.html#horizontal-filtering-rows

        For example, if you want to filter on a specific `campaign_id`, you would pass `eq.12345` to the `campaign_id` param
        where `12345` is the campaign id.

        `Args:`
            id: string <integer>
                The ID of the subscription event
            member_id: string <integer>
                The ID of the member in question
            type: string <text>
                The type of event which lead to the subscription or unsubscription
            created_at: string <timestamp with time zone>
                When the event occurred
            ref_id: string <integer>
                ID of upload, status code, incoming message, or other relevant artifact of subscription event
            supplemental: string <text>
                Supplemental information about the event
            unsubscribe: string <boolean>
                Whether the member has been unsubscribed
            campaign_id: string <integer>
                The ID of the campaign associated with this event
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
        full_url = self.build_url(kwargs, "subscription_events")

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
            id: string <integer>
                The ID of the member
            campaign_id: string <integer>
                The campaign associated with the member
            phone_number: string <character varying>
                The member's phone number
            first_name: string <character varying>
                The member's first name
            last_name: string <character varying>
                The member's last name
            city: string <character varying>
                The City associated with the member
            state: string <character varying>
                The State assoicated with the member
            postal_code: string <character varying>
                The zip or postcal code assoicated with the member
            email: string <character varying>
                The member's email address
            notes: string <text>
                The content of notes associated with the member
            additional_notes: string <text>
                The content of additional notes field associated with the member
            opt_in: string <boolean>
                Whether or not the member is subscribed to recieve further messages
            custom: string <jsonb>
                The custom fields associated with the member
            created_at: string <timestamp with time zone>
                When the member was either first imported or opted-in to recieve messages
            updated_at: string <timestamp with time zone>
                When the member was last updated with a change
            group: string <json>
                Groups this member belongs to (json)
            carrier: string <text>
                The mobile carrier this member uses
            first_sub_id: string <integer>
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

    def post_members(self, payload):
        """
        Sends a POST request to the /members endpoint with a given payload.
        To learn more about POST requests to Strive's member endpoint, go here:
        https://developers.strivemessaging.org/#tag/members/paths/~1members/post

        """

        # Send the POST request
        response = self.client.post_request(data=json.dumps(payload))

        # Convert the API response to a Parsons Table object
        table = Table(response)
        return table

    def get_incoming_messages(self, **kwargs):
        """
        Sends a GET request to the /incoming_messages endpoint with specified parameters,
        and returns the response in a Table object.

        The Strive connector uses horizontal filtering. You can learn more about
        horizontal filtering here: https://postgrest.org/en/stable/references/api/tables_views.html#horizontal-filtering-rows

        For example, if you want to filter on a specific `campaign_id`, you would pass `eq.12345` to the `campaign_id` param
        where `12345` is the campaign id.

        `Args:`
            id: string <integer>
                The ID of the incoming message
            campaign_id: string <integer>
                The campaign associated with the outgoing message
            member_id: string <integer>
                The member targeted by the outgoing message
            from_number: string <character varying>
                The member's phone number
            to_number: string <character varying>
                The phone number the member targeted
            message: string <character varying>
                The contents of the outgoing message
            attachments: string <json>
                The attachement, or MMS included in the incoming message
            sent_at: string <timestamp with time zone>
                When the outgoing message was sent
            is_opt_out: string <boolean>
                Whether or not the message was registerted as a request to unsubscribe from further messages
            updated_at: string <timestamp with time zone>
                When the message was updated
            conversation_id: string <integer>
                The id of the conversation that this message belongs to
            flow_id: string <integer>
                The flow that the message belongs to
            step_idx: string <integer>
                The step in the flow this message corresponds to
            response_to_id: string <integer>
                The id of the broadcast the incoming message was a response to
            select: str
                Filtering Columns
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
        full_url = self.build_url(kwargs, "outgoing_messages")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table

    def get_broadcasts_groups(self, **kwargs):
        """
        Sends a GET request to the /broadcasts_groups endpoint with specified parameters,
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

    def get_campaigns():
        """
        Sends a GET request to the /campaigns endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: string <integer>
                The ID of the campaign
            primary_text_in_number: string <character varying>
                The phone number new supporters can text to become a member
            is_active: string <boolean>
                The status of the campaign's subscription
            custom_fields: string <json>
                Custom fields added or active to the campaign
            organization_id: string <integer>
                The ID of the parent account, which the campaign is part of
            name: string <character varying>
                The name of the campaign
            updated_at: string <timestamp with time zone>
                When the campaign was last updated
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
        full_url = self.build_url(kwargs, "campaigns")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table
    
    def get_flows():
        """
        Sends a GET request to the /campaigns endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: string <integer>
                The ID of the flow
            campaign_id: string <integer>
                The campaign associated with the flow
            name: string <chracter varying>
                The name of the flow
            created_at: string <timestamp with time zone>
                When the flow was first created
            updated_at: string <timestamp with time zone>
                When the flow was last updated with a change
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
        full_url = self.build_url(kwargs, "flows")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table
    
    def get_members_custom_fields():
        """
        Sends a GET request to the /members_custom_fields endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: string <integer>
                The ID of the custom field associated with a member
            field: string <text>
                The name of the field in the API
            value: string <jsonb>
                The value of the field
            updated_at: string <timestamp with time zone>
                When this custom value was updated
            campaign_id: string <integer>
                The campaign the value belongs to
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
        full_url = self.build_url(kwargs, "members_custom_fields")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table
    
    def get_broadcasts():
        """
        Sends a GET request to the /broadcasts endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: string <integer>
                The ID of the Broadcast
            user_id: string <integer>
                The Strive user who sent the broadcast
            campaign_id: string <integer>
                The campaign that the broadcast belongs to
            flow_id: string <integer>
                The flow that was broadcasted
            name: string <text>
                The name of the Broadcast
            message: string <text>
                The content of the first message sent in the broadcast
            attachment: string <text>
                The attachment or MMS included in the broadcast
            recipient_count: string <integer>
                How many members were targeted for the broadcast
            scheduled_at: string <timestamp with time zone>
                When the broadcast is scheduled to send
            cancelled_at: string <timestamp with time zone>
                When the broadcast was cancelled
            sent_at: string <timestamp with time zone>
                When the broadcast began to deliver
            created_at: string <timestamp with time zone>
                When the broadcast was first created
            updated_at: string <timestamp with time zone>
                When the broadcast was last updated
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
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

    def get_members_links():
        """
        Sends a GET request to the /members_links endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: string <integer>
                The ID of the member_link
            link_id: string <integer>
                The link this member_link references
            member_id: string <integer>
                The member the link was sent to
            outgoing_message_id: string <integer>
                The outgoing message in which this link was sent
            broadcast_id: string <integer>
                The broadcast in which this link was sent
            url: string <text>
                The url that the trackable link directed to
            was_visited: string <boolean>
                Whether or not the member visited the link
            created_at: string <timestamp with time zone>
                When the link was sent to the member
            updated_at: string <timestamp with time zone>
                When the link was last updated
            visited_at: string <timestamp with time zone>
                When the member visited the link
            crawled_at: string <timestamp with time zone>
                When an automated process visited the link
            user_agent: string <text>
                The user agent string recorded when the link was visited
            visitor_ip: string <text>
                The IP address recorded when the link was visited
            campaign_id: string <integer>
                The campaign this link belongs to
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /broadcasts endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Build URL
        full_url = self.build_url(kwargs, "members_links")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table

    def get_groups():
        """
        Sends a GET request to the /groups endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: string <integer>
                The ID of the group
            name: string <character varying>
                The name of the group
            campaign_id: string <integer>
                The campaign associated with the group
            created_at: string <timestamp with time zone>
                The outgoing messagWhen the group was first created
            updated_at: string <timestamp with time zone>
                When the group was last updated with a change
            keyword: string <character varying>
                The keyword that, when used by members, adds members to the group
            synonyms: string <character varying>
                The synonyms of the keyword that, when used by members, adds members to the group
            flow_id: string <integer>
                The flow that is sent to members when they join the group
            groupable_type: string <app_public.groupable>
                The type of attribute or relationship on which members are added to the group
            groupable_id: string <integer>
                The identifier of the attribute or relationship on which members are added to the group
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /broadcasts endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Build URL
        full_url = self.build_url(kwargs, "groups")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table

    def get_organizations():
        """
        Sends a GET request to the /organizations endpoint with specified parameters,
        and returns the response in a Table object.

        `Args:`
            id: string <integer>
                The ID of the organization
            name: string <character varying>
                The name of the organization
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /broadcasts endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Build URL
        full_url = self.build_url(kwargs, "organizations")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table

    def get_member_group_delete_log():
        """
        Sends a GET request to the /member_group_delete_log endpoint with specified parameters,
        and returns the response in a Table object. this endpoint represents an organization's records on when members are removed from groups

        `Args:`
            group_id: string <integer>
                The ID of the organization
            campaign_id: string <integer>
                The campaign associated with the group and member
            member_id: string <integer>
                The member that has been removed
            member_added_on: string <integer>
                Date that the member was added to the group
            delete_source: string <integer>
                The general source of the member being removed from the group
            delete_source_id: string <integer>
                The id of the source of the member group removal if there is one
            removed_by: string <integer>
                The admin/orgainzer that removed the member of the group if there was 
            member_removed_on: string <integer>
                Date that the member was removed from the group
            name: string <character varying>
                The name of the organization
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /broadcasts endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Build URL
        full_url = self.build_url(kwargs, "member_group_delete_log")

        # Send the GET request
        response = self.client.get_request(url=full_url)

        # Process the response
        table = Table(response)
        return table


# Testing
# strive = Strive()
# strive.get_members(first_name = 'eq.brittany')

# in the docs, youw ant to pass params like this, here is an example.
# then add link to their documentation
