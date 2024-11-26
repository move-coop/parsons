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
            id: string <integer>
                The ID of the P2P message.
            user_id: string <integer>
                The ID of the user who created the P2P message.
            campaign_id: string <integer>
                The ID of the campaign that the P2P message is associated with.
            message: string <text>
                The text content of the P2P message.
            attachment: string <text>
                A URL to an attachment that was sent with the P2P message.
            scheduled_at: string <timestamp with time zone>
                The date and time that the P2P message is scheduled to be sent.
            cancelled_at: string <timestamp with time zone>
                The date and time that the P2P message was cancelled, if applicable.
            sent_at: string <timestamp with time zone>
                The date and time that the P2P message was sent, if applicable.
            created_at: string <timestamp with time zone>
                The date and time that the P2P message was created.
            updated_at: string <timestamp with time zone>
                The date and time that the P2P message was last updated.
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /p2ps endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Send the GET request
        response = self.client.get_request(url="p2ps", params=kwargs)

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
            campaign_id: string <integer>
                The ID of the campaign that the P2P message is associated with.
            field: string <text>
                The name of the field within the API
            label: string <text>
                The name of the field within the product
            type: string <text>
                The type of field the custom field is
            updated_at: string <timestamp with time zone>
                The date and time that the P2P message was last updated.
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /p2ps endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Send the GET request
        response = self.client.get_request("custom_fields", params=kwargs)

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
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /p2ps endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """
        # Send the GET request
        response = self.client.get_request("outgoing_messages", params=kwargs)

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
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /p2ps endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Send the GET request
        response = self.client.get_request("subscription_events", params=kwargs)

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
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /p2ps endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.

        """

        # Send the GET request
        response = self.client.get_request(url="/members", params=kwargs)
        
        # Convert the API response to a Parsons Table object
        table = Table(response)
        return table

    def post_members(self, data):
        """
        Sends a POST request to the /members endpoint with a given payload.
        To learn more about POST requests to Strive's member endpoint, go here:
        https://developers.strivemessaging.org/#tag/members/paths/~1members/post

        """

        # Send the POST request
        response = self.client.post_request(url="/members", data=data)

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
            select: string
                Filtering Columns
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /p2ps endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Send the GET request
        response = self.client.get_request(url="outgoing_messages", params=kwargs)

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
            select: string
                The fields to include in the response. Use comma-separated values to include multiple fields.
            order: string
                The field to use for sorting the response. Use a minus sign (-) prefix to sort in descending order.
            offset: string
                The number of records to skip before returning results.
            limit: string
                The maximum number of records to return.

        `Returns:`
            parsons.Table: A Parsons Table object containing the response data from the /broadcasts_groups endpoint.

        `Raises:`
            ValueError: If any of the filter parameters have an invalid data type.
        """

        # Send the GET request
        response = self.client.get_request(url="broadcast_groups", params=kwargs)

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

        # Send the GET request
        response = self.client.get_request(url="campaigns", params=kwargs)

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

        # Send the GET request
        response = self.client.get_request(url="flows", params=kwargs)

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

        # Send the GET request
        response = self.client.get_request(url="members_custom_fields", params=kwargs)

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

        # Send the GET request
        response = self.client.get_request(url="broadcasts", params=kwargs)

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

        # Send the GET request
        response = self.client.get_request(url="members_links", params=kwargs)

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

        # Send the GET request
        response = self.client.get_request(url="groups", params=kwargs)

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

        # Send the GET request
        response = self.client.get_request(url="organizations", params=kwargs)

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

        # Send the GET request
        response = self.client.get_request(url="member_group_delete_log", params=kwargs)

        # Process the response
        table = Table(response)
        return table

    def get_call_logs():
        """
        Sends a GET request to the /call_logs endpoint with specified parameters,
        and returns the response in a Table object. This endpoint represents each call queued or connected through the campaign.

        `Args:`
            id: string <integer>
                The ID of the call log
            campaign_id: string <integer>
                The ID of the campaign for which the call was connected
            member_id: string <integer>
                The ID of the member for whom the call was connected
            call_target_id: string <integer>
                The ID of the call target
            bot_conversation_id: string <integer>
                The ID of the bot conversation from which the call, or call invitation, was dispatched
            call_number_id: string <integer>
                The ID of the call number
            from_number: string <integer>
                The number of the member for whom the call was connected
            to_number: string <integer>
                The number to which the call was connected
            machine_detected: string <character varying>
                Whether an answering machine was detected after connecting to the target
            successful_connection: string <integer>
                Whether a successful connection was made to the member
            created_at: string <integer>
                When the target was first looked up and the call queued
            connected_at: string <integer>
                When the call connected to the member
            redirected_at: string <integer>
                When the call redirected to the target
            ended_at: string <integer>
                    When the call ended
            updated_at: string <integer>
            flow_id: string <integer>
                The flow of which this call was a part
            step_idx: string <integer>  
                The step of the flow in which this call took place
            office: string <integer>
                The office of the target contacted
            state: string <integer>
                The state in which the target exists
            party: string <integer>
                The party of the target
            name: string <integer>
                The name of the target
            member_voicemail_answered_at: string <integer>
                The time at which the voicemail of the member picked up
            member_call_failed_at: string <integer>
                The time at which the call to the member failed
            target_call_failed_at: string <integer>
                The time at which the call to the target failed
            last_event: string <integer>
                The status of the call based on last event recorded
            broadcast_id: string <integer>
                The broadcast in which the call was made
            call_number: string <integer>
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

        # Send the GET request
        response = self.client.get_request(url="call_logs", params=kwargs)

        # Process the response
        table = Table(response)
        return table

    def get_member_change_log(self, **kwargs):
        """
        Sends a GET request to the /member_change_log endpoint with specified parameters,
        and returns the response in a Table object. This endpoint represents Organization's change data as it relates to member fields.

        `Args:`
            member_id: string <integer>
                The ID of the member
            campaign_id: string <integer>
                The campaign associated with the member
            change_action: string <character varying>
                The action that changed the previous value to the new value
            previous_value: string <jsonb>
                The previous value for the field(s) denoted in the object
            new_value: string <jsonb>
                The new value for the field(s) denoted in the object
            change_type: string <text>
                The source of the member change
            change_value: string <text>
                The value of the source of the member change
            updated_at: string <timestamp with time zone>
                The date and time at which this member value was created
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

        # Send the GET request
        response = self.client.get_request(url="member_change_log", params=kwargs)

        # Process the response
        table = Table(response)
        return table

    def get_enhanced_member_data(self, **kwargs):
        """
        Sends a GET request to the /enhanced_member_data endpoint with specified parameters,
        and returns the response in a Table object. This endpoint represents organization's member data populated through Strive automations

        `Args:`
            id: string <integer>
            member_id: string <integer>
                The ID of the member
            campaign_id: string <character varying>
                The campaign associated with the member
            federal_house_district: string <character varying>
                The federal district for the member
            state_upper_chamber_district: string <character varying>
                The district of the upper state chamber
            state_lower_chamber_district: string <character varying>
                The district of the lower state chamber
            created_at: string <timestamp with time zone>
                When this member's Strive data was first populated
            updated_at: string <timestamp with time zone>
                The last time we updated a member's automated data
            federal_representative: string <text>
                The member's federal representative
            federal_senator_one: string <text>
                One member's federal senator
            federal_senator_two: string <text>
                The other federal senator for the member
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

        # Send the GET request
        response = self.client.get_request(url="enhanced_member_data", params=kwargs)

        # Process the response
        table = Table(response)
        return table

    def get_flow_actions(self, **kwargs):
        """
        Sends a GET request to the /flow_actions endpoint with specified parameters,
        and returns the response in a Table object. This endpoint represents actions taken by members when interacting with flows

        `Args:`
            id: string <integer>
            flow_id: string <integer>
                The flow associated with the action
            member_id: string <character varying>
                The member who took the action
            incoming_message_id: string <character varying>
                The message the member responded wtih
            step_number: string <character varying>
                The position of the message within the flow sequence
            is_response_valid: string <character varying>
                Whether or not the member's response was successfully qualified
            collected_value: string <timestamp with time zone>
                The data successfully parsed and mapped by the flow's "Collect"
            created_at: string <timestamp with time zone>
                When the flow action occurred
            updated_at: string <text>
                When the flow action was updated, usually the same as created
            campaign_id: string <text>
                The campaign the flow action belongs to
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

        # Send the GET request
        response = self.client.get_request(url="flow_actions", params=kwargs)

        # Process the response
        table = Table(response)
        return table

    def get_group_members(self, **kwargs):
        """
        Sends a GET request to the /groups_members endpoint with specified parameters,
        and returns the response in a Table object. This endpoint represents members in a group.

        `Args:`
            member_id: string <integer>
                The ID of the member
            group_id: string <integer>
                The ID of ther group
            created_at: string <timestamp with time zone>>
                When the group membership was created
            updated_at: string <timestamp with time zone>>
                When the group membership was updated
            organizer_ids: string <integer>
            campaign_id: string <integer>
                The campaign that the group and member belong to
            user_id: string <integer>
                The ID of the user that added the member to the group
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

        # Send the GET request
        response = self.client.get_request(url="groups_members", params=kwargs)

        # Process the response
        table = Table(response)
        return table

    def get_flow_steps(self, **kwargs):
        """
        Sends a GET request to the /flow_steps endpoint with specified parameters,
        and returns the response in a Table object. This endpoint represents the steps within a flow sequence

        `Args:`
            flow_id: string <integer>
                The flow associated with the flow step
            step_number: string <integer>
                The position of the flow step within the larger flow sequence
            type: string <text>>
                The type of the step, typically one of these three types: Simple, Collect Info, or Ask A Question type
            message: string <text>
                The content of the message inlcuded in the flow step
            updated_at: string <timestamp with time zone>
                When this flow was last updated
            campaign_id: string <integer>
                The campaign the flow step belongs to
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

        # Send the GET request
        response = self.client.get_request(url="flow_steps", params=kwargs)

        # Process the response
        table = Table(response)
        return table
