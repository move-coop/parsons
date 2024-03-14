import logging
import re
from parsons.etl import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)


class Mailchimp:
    """
    Instantiate Mailchimp Class

    `Args:`
        api_key:
            The Mailchimp-provided application key. Not required if
            ``MAILCHIMP_API_KEY`` env variable set.
    `Returns:`
        Mailchimp Class
    """

    def __init__(self, api_key=None):
        self.api_key = check_env.check("MAILCHIMP_API_KEY", api_key)
        self.domain = re.findall("(?<=-).+$", self.api_key)[0]
        self.uri = f"https://{self.domain}.api.mailchimp.com/3.0/"
        self.client = APIConnector(self.uri, auth=("x", self.api_key))

    def get_lists(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        before_date_created=None,
        since_date_created=None,
        before_campaign_last_sent=None,
        since_campaign_last_sent=None,
        email=None,
        sort_field=None,
        sort_dir=None,
    ):
        """
        Get a table of lists under the account based on query parameters. Note
        that argument descriptions here are sourced from Mailchimp's official
        API documentation.

        `Args:`
            fields: list of strings
                A comma-separated list of fields to return. Reference
                parameters of sub-objects with dot notation.
            exclude_fields: list of strings
                A comma-separated list of fields to exclude. Reference
                parameters of sub-objects with dot notation.
            count: int
                The number of records to return. Default value is 10. Maximum
                value is 1000.
            offset: int
                The number of records from a collection to skip. Iterating over
                large collections with this parameter can be slow. Default
                value is 0.
            before_date_created: string
                Restrict response to lists created before the set date. We
                recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00.
            since_date_created: string
                Restrict results to lists created after the set date. We
                recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00.
            before_campaign_last_sent: string
                Restrict results to lists created before the last campaign send
                date. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00.
            since_campaign_last_sent: string
                Restrict results to lists created after the last campaign send
                date. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00.
            email: string
                Restrict results to lists that include a specific subscriber's
                email address.
            sort_field: string, can only be 'date_created' or None
                Returns files sorted by the specified field.
            sort_dir: string, can only be 'ASC', 'DESC', or None
                Determines the order direction for sorted results.

        `Returns:`
            Table Class
        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
            "before_date_created": before_date_created,
            "since_date_created": since_date_created,
            "before_campaign_last_sent": before_campaign_last_sent,
            "since_campaign_last_sent": since_campaign_last_sent,
            "email": email,
            "sort_field": sort_field,
            "sort_dir": sort_dir,
        }

        response = self.client.get_request("lists", params=params)
        tbl = Table(response["lists"])
        logger.info(f"Found {tbl.num_rows} lists.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_campaigns(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        type=None,
        status=None,
        before_send_time=None,
        since_send_time=None,
        before_create_time=None,
        since_create_time=None,
        list_id=None,
        folder_id=None,
        member_id=None,
        sort_field=None,
        sort_dir=None,
    ):
        """
        Get a table of campaigns under the account based on query parameters.
        Note that argument descriptions here are sourced from Mailchimp's
        official API documentation.

        `Args:`
            fields: list of strings
                A comma-separated list of fields to return. Reference
                parameters of sub-objects with dot notation.
            exclude_fields: list of strings
                A comma-separated list of fields to exclude. Reference
                parameters of sub-objects with dot notation.
            count: int
                The number of records to return. Default value is 10. Maximum
                value is 1000.
            offset: int
                The number of records from a collection to skip. Iterating over
                large collections with this parameter can be slow. Default
                value is 0.
            type: string, can only be 'regular', 'plaintext', 'absplit', 'rss',
            'variate', or None
                The campaign type.
            status: string, can only be 'save', 'paused', 'schedule',
            'sending', 'sent', or None
                The status of the campaign.
            before_send_time: string
                Restrict the response to campaigns sent before the set time. We
                recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00.
            since_send_time: string
                Restrict the response to campaigns sent after the set time. We
                recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00.
            before_create_time: string
                Restrict the response to campaigns created before the set time.
                We recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00.
            since_create_time: string
                Restrict the response to campaigns created after the set time.
                We recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00.
            list_id: string
                The unique id for the list.
            folder_id: string
                The unique folder id.
            member_id: string
                Retrieve campaigns sent to a particular list member. Member ID
                is The MD5 hash of the lowercase version of the list member’s
                email address.
            sort_field: string, can only be 'create_time', 'send_time', or None
                Returns files sorted by the specified field.
            sort_dir: string, can only be 'ASC', 'DESC', or None
                Determines the order direction for sorted results.

        `Returns:`
            Table Class
        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
            "type": type,
            "status": status,
            "before_send_time": before_send_time,
            "since_send_time": since_send_time,
            "before_create_time": before_create_time,
            "since_create_time": since_create_time,
            "list_id": list_id,
            "folder_id": folder_id,
            "member_id": member_id,
            "sort_field": sort_field,
            "sort_dir": sort_dir,
        }

        response = self.client.get_request("campaigns", params=params)
        tbl = Table(response["campaigns"])
        logger.info(f"Found {tbl.num_rows} campaigns.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_members(
        self,
        list_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        email_type=None,
        status=None,
        since_timestamp_opt=None,
        before_timestamp_opt=None,
        since_last_changed=None,
        before_last_changed=None,
        unique_email_id=None,
        vip_only=False,
        interest_category_id=None,
        interest_ids=None,
        interest_match=None,
        sort_field=None,
        sort_dir=None,
        since_last_campaign=None,
        unsubscribed_since=None,
    ):
        """
        Get a table of members in a list based on query parameters. Note that
        argument descriptions here are sourced from Mailchimp's official API
        documentation.

        `Args:`
            list_id: string
                The unique ID of the list to fetch members from.
            fields: list of strings
                A comma-separated list of fields to return. Reference
                parameters of sub-objects with dot notation.
            exclude_fields: list of fields as strings
                A comma-separated list of fields to exclude. Reference
                parameters of sub-objects with dot notation.
            count: int
                The number of records to return. Default value is 10. Maximum
                value is 1000.
            offset: int
                The number of records from a collection to skip. Iterating over
                large collections with this parameter can be slow. Default
                value is 0.
            email_type: string
                The email type.
            status: string, can only be 'subscribed', 'unsubscribed',
            'cleaned', 'pending', 'transactional', 'archived', or None
                The subscriber's status.
            since_timestamp_opt: string
                Restrict results to subscribers who opted-in after the set
                timeframe. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00.
            before_timestamp_opt: string
                Restrict results to subscribers who opted-in before the set
                timeframe. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00.
            since_last_changed: string
                Restrict results to subscribers whose information changed after
                the set timeframe. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00.
            before_last_changed: string
                Restrict results to subscribers whose information changed
                before the set timeframe. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00.
            unique_email_id: string
                A unique identifier for the email address across all Mailchimp
                lists. This parameter can be found in any links with Ecommerce
                Tracking enabled.
            vip_only: boolean
                A filter to return only the list's VIP members. Passing true
                will restrict results to VIP list members, passing false will
                return all list members.
            interest_category_id: string
                The unique id for the interest category.
            interest_ids: list of strings
                Used to filter list members by interests. Must be accompanied
                by interest_category_id and interest_match. The value must be a
                comma separated list of interest ids present for any supplied
                interest categories.
            interest_match: string, can only be 'any', 'all', 'none', or None
                Used to filter list members by interests. Must be accompanied
                by interest_category_id and interest_ids. "any" will match a
                member with any of the interest supplied, "all" will only match
                members with every interest supplied, and "none" will match
                members without any of the interest supplied.
            sort_field: string, can only be 'timestamp_opt',
            'timestamp_signup', 'last_changed', or None
                Returns files sorted by the specified field.
            sort_dir: string, can only be 'ASC', 'DESC', or None
                Determines the order direction for sorted results.
            since_last_campaign: string
                Filter subscribers by those
                subscribed/unsubscribed/pending/cleaned since last email
                campaign send. Member status is required to use this filter.
            unsubscribed_since: string
                Filter subscribers by those unsubscribed since a specific date.
                Using any status other than unsubscribed with this filter will
                result in an error.

        `Returns:`
            Table Class
        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
            "email_type": email_type,
            "status": status,
            "since_timestamp_opt": since_timestamp_opt,
            "before_timestamp_opt": before_timestamp_opt,
            "since_last_changed": since_last_changed,
            "before_last_changed": before_last_changed,
            "unqiue_email_id": unique_email_id,
            "vip_only": vip_only,
            "interest_category_id": interest_category_id,
            "interest_ids": interest_ids,
            "interest_match": interest_match,
            "sort_field": sort_field,
            "sort_dir": sort_dir,
            "since_last_campaign": since_last_campaign,
            "unsubscribed_since": unsubscribed_since,
        }

        response = self.client.get_request(f"lists/{list_id}/members", params=params)
        tbl = Table(response["members"])
        logger.info(f"Found {tbl.num_rows} members.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_campaign_emails(
        self,
        campaign_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        since=None,
    ):
        """
        Get a table of individual emails from a campaign based on query
        parameters. Note that argument descriptions here are sourced from
        Mailchimp's official API documentation.

        `Args:`
            campaign_id: string
                The unique ID of the campaign to fetch emails from.
            fields: list of strings
                A comma-separated list of fields to return. Reference
                parameters of sub-objects with dot notation.
            exclude_fields: list of strings
                A comma-separated list of fields to exclude. Reference
                parameters of sub-objects with dot notation.
            count: int
                The number of records to return. Default value is 10. Maximum
                value is 1000.
            offset: int
                The number of records from a collection to skip. Iterating over
                large collections with this parameter can be slow. Default
                value is 0.
            since: string
                Restrict results to email activity events that occur after a
                specific time. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00.

        `Returns:`
            Table Class
        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
            "since": since,
        }

        response = self.client.get_request(f"reports/{campaign_id}/email-activity", params=params)
        tbl = Table(response["emails"])
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_unsubscribes(
        self, campaign_id, fields=None, exclude_fields=None, count=None, offset=None
    ):
        """
        Get a table of unsubscribes associated with a campaign based on query
        parameters. Note that argument descriptions here are sourced from
        Mailchimp's official API documentation.

        `Args:`
            campaign_id: string
                The unique ID of the campaign to fetch unsubscribes from.
            fields: list of strings
                A comma-separated list of fields to return. Reference
                parameters of sub-objects with dot notation.
            exclude_fields: list of strings
                A comma-separated list of fields to exclude. Reference
                parameters of sub-objects with dot notation.
            count: int
                The number of records to return. Default value is 10. Maximum
                value is 1000.
            offset: int
                The number of records from a collection to skip. Iterating over
                large collections with this parameter can be slow. Default
                value is 0.

        `Returns:`
            Table Class
        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
        }

        response = self.client.get_request(f"reports/{campaign_id}/unsubscribed", params=params)
        tbl = Table(response["unsubscribes"])
        logger.info(f"Found {tbl.num_rows} unsubscribes for {campaign_id}.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()
