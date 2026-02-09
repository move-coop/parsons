import logging
import re
from typing import Literal

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)


class Mailchimp:
    """
    Instantiate Mailchimp Class.

    Args:
        api_key: The Mailchimp-provided application key. Not required if
            ``MAILCHIMP_API_KEY`` env variable set. Defaults to None.

    Returns:
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
        Get a table of lists under the account based on query parameters.

        Note that argument descriptions here are sourced from Mailchimp's official API documentation.

        Args:
            fields: List of strings A comma-separated list of fields to return. Reference parameters of sub-objects
                with dot notation. Defaults to None.
            exclude_fields: List of strings A comma-separated list of fields to exclude. Reference parameters of
                sub-objects with dot notation. Defaults to None.
            count (int, optional): The number of records to return. Default value is 10. Maximum value is 1000.
                Defaults to None.
            offset (int, optional): The number of records from a collection to skip. Iterating over large
                collections with this parameter can be slow. Default value is 0. Defaults to None.
            before_date_created (str, optional): Restrict response to lists created before the set date.
                We recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00. Defaults to None.
            since_date_created (str, optional): Restrict results to lists created after the set date.
                We recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00. Defaults to None.
            before_campaign_last_sent (str, optional): Restrict results to lists created before the last campaign
                send date. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00. Defaults to None.
            since_campaign_last_sent (str, optional): Restrict results to lists created after the last campaign send
                date. We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00. Defaults to None.
            email (str, optional): Restrict results to lists that include a specific subscriber's email address.
                Defaults to None.
            sort_field: String, can only be 'date_created' or None Returns files sorted by the specified field.
                Defaults to None.
            sort_dir: String, can only be 'ASC', 'DESC', or None Determines the order direction for sorted results.
                Defaults to None.

        Returns:
            Table

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
        type: Literal["regular", "plaintext", "absplit", "rss", "variate"] | None = None,
        status: Literal["save", "paused", "schedule", "sending", "sent"] | None = None,
        before_send_time=None,
        since_send_time=None,
        before_create_time=None,
        since_create_time=None,
        list_id=None,
        folder_id=None,
        member_id=None,
        sort_field: Literal["create_time", "send_time"] | None = None,
        sort_dir: Literal["asc", "desc"] | None = None,
    ):
        """
        Get a table of campaigns under the account based on query parameters.

        Note that argument descriptions here are sourced from Mailchimp's official API documentation.

        Args:
            fields: List[str] A comma-separated list of fields to return. Reference parameters of sub-objects with
                dot notation. Defaults to None.
            exclude_fields: List[str] A comma-separated list of fields to exclude. Reference parameters of
                sub-objects with dot notation. Defaults to None.
            count (int, optional): The number of records to return. Default value is 10. Maximum value is 1000.
                Defaults to None.
            offset (int, optional): The number of records from a collection to skip. Iterating over large
                collections with this parameter can be slow. Default value is 0. Defaults to None.
            type (Literal["regular", "plaintext", "absplit", "rss", "variate"] | None, optional): The campaign type.
                Defaults to None.
            status (Literal["save", "paused", "schedule", "sending", "sent"] | None, optional): The status of the
                campaign. Defaults to None.
            before_send_time (str, optional): Restrict the response to campaigns sent before the set time.
                We recommend ISO 8601 time format ``2015-10-21T15:41:36+00:00``. Defaults to None.
            since_send_time (str, optional): Restrict the response to campaigns sent after the set time.
                We recommend ISO 8601 time format ``2015-10-21T15:41:36+00:00``. Defaults to None.
            before_create_time (str, optional): Restrict the response to campaigns created before the set time.
                We recommend ISO 8601 time format ``2015-10-21T15:41:36+00:00``. Defaults to None.
            since_create_time (str, optional): Restrict the response to campaigns created after the set time.
                We recommend ISO 8601 time format ``2015-10-21T15:41:36+00:00``. Defaults to None.
            list_id (str, optional): The unique id for the list. Defaults to None.
            folder_id (str, optional): The unique folder id. Defaults to None.
            member_id (str, optional): Retrieve campaigns sent to a particular list member.
                Member ID is the MD5 hash of the lowercase version of the list member's email address.
                Defaults to None.
            sort_field (Literal["create_time", "send_time"] | None, optional): Returns files sorted by the specified
                field. Defaults to None.
            sort_dir (Literal["asc", "desc"] | None, optional): Determines the order direction for sorted results.
                Defaults to None.

        Returns:
            Table

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
        status: Literal[
            "subscribed", "unsubscribed", "cleaned", "pending", "transactional", "archived"
        ]
        | None = None,
        since_timestamp_opt=None,
        before_timestamp_opt=None,
        since_last_changed=None,
        before_last_changed=None,
        unique_email_id=None,
        vip_only=False,
        interest_category_id=None,
        interest_ids=None,
        interest_match: Literal["any", "all", "none"] | None = None,
        sort_field: Literal["timestamp_opt", "timestamp_signup", "last_changed"] | None = None,
        sort_dir: Literal["asc", "desc"] | None = None,
        since_last_campaign=None,
        unsubscribed_since=None,
    ) -> Table:
        """
        Get a table of members in a list based on query parameters.

        Note that argument descriptions here are sourced from Mailchimp's official API documentation.

        Args:
            list_id (str): The unique ID of the list to fetch members from.
            fields: List[str] A comma-separated list of fields to return. Reference parameters of sub-objects with
                dot notation. Defaults to None.
            exclude_fields: List[str] A comma-separated list of fields to exclude. Reference parameters of
                sub-objects with dot notation. Defaults to None.
            count (int, optional): The number of records to return. Default value is 10. Maximum value is 1000.
                Defaults to None.
            offset (int, optional): The number of records from a collection to skip. Iterating over large
                collections with this parameter can be slow. Default value is 0. Defaults to None.
            email_type (str, optional): The email type. Defaults to None.
            status (Literal["subscribed", "unsubscribed", "cleaned", "pending", "transactional", "archived"], optional):
                The subscriber's status. Defaults to None.
            since_timestamp_opt (str, optional): Restrict results to subscribers who opted-in after the set
                timeframe. We recommend ISO 8601 time format ``2015-10-21T15:41:36+00:00``. Defaults to None.
            before_timestamp_opt (str, optional): Restrict results to subscribers who opted-in before the set
                timeframe. We recommend ISO 8601 time format ``2015-10-21T15:41:36+00:00``. Defaults to None.
            since_last_changed (str, optional): Restrict results to subscribers whose information changed after the
                set timeframe. We recommend ISO 8601 time format
                ``2015-10-21T15:41:36+00:00``. Defaults to None.
            before_last_changed (str, optional): Restrict results to subscribers whose information changed before
                the set timeframe. We recommend ISO 8601 time format
                ``2015-10-21T15:41:36+00:00``. Defaults to None.
            unique_email_id (str, optional): A unique identifier for the email address across all Mailchimp lists.
                This parameter can be found in any links with Ecommerce Tracking enabled. Defaults to None.
            vip_only (bool, optional): A filter to return only the list's VIP members. Passing true will restrict
                results to VIP list members, passing false will return all list members. Defaults to False.
            interest_category_id (str, optional): The unique id for the interest category.
                Defaults to None.
            interest_ids: List[str] Used to filter list members by interests. Must be accompanied by
                interest_category_id and interest_match. The value must be a comma separated list of interest ids
                present for any supplied interest categories. Defaults to None.
            interest_match (Literal["any", "all", "none"] | None, optional):
                Used to filter list members by interests. Must be accompanied by
                interest_category_id and interest_ids.
                - "any" will match a member with any of the interest supplied
                - "all" will only match members with every interest supplied
                - "none" will match members without any of the interest supplied. Defaults to None.
            sort_field (Literal["timestamp_opt", "timestamp_signup", "last_changed"] | None, optional):
                Returns files sorted by the specified field. Defaults to None.
            sort_dir (Literal["asc", "desc"] | None, optional): Determines the
                order direction for sorted results. Defaults to None.
            since_last_campaign (str, optional): Filter subscribers by those subscribed/unsubscribed/pending/cleaned
                since last email campaign send. Member status is required to use this filter. Defaults to None.
            unsubscribed_since (str, optional): Filter subscribers by those unsubscribed since a specific date.
                Using any status other than unsubscribed with this filter will result in an error.
                Defaults to None.

        Returns:
            Table

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
        Get a table of individual emails from a campaign based on query parameters.

        Note that argument descriptions here are sourced from Mailchimp's official API documentation.

        Args:
            campaign_id (str): The unique ID of the campaign to fetch emails from.
            fields: List of strings A comma-separated list of fields to return. Reference parameters of sub-objects
                with dot notation. Defaults to None.
            exclude_fields: List of strings A comma-separated list of fields to exclude. Reference parameters of
                sub-objects with dot notation. Defaults to None.
            count (int, optional): The number of records to return. Default value is 10. Maximum value is 1000.
                Defaults to None.
            offset (int, optional): The number of records from a collection to skip. Iterating over large
                collections with this parameter can be slow. Default value is 0. Defaults to None.
            since (str, optional): Restrict results to email activity events that occur after a specific time.
                We recommend ISO 8601 time format:
                2015-10-21T15:41:36+00:00. Defaults to None.

        Returns:
            Table

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
        Get a table of unsubscribes associated with a campaign based on query parameters.

        Note that argument descriptions here are sourced from Mailchimp's official API documentation.

        Args:
            campaign_id (str): The unique ID of the campaign to fetch unsubscribes from.
            fields: List of strings A comma-separated list of fields to return. Reference parameters of sub-objects
                with dot notation. Defaults to None.
            exclude_fields: List of strings A comma-separated list of fields to exclude. Reference parameters of
                sub-objects with dot notation. Defaults to None.
            count (int, optional): The number of records to return. Default value is 10. Maximum value is 1000.
                Defaults to None.
            offset (int, optional): The number of records from a collection to skip. Iterating over large
                collections with this parameter can be slow. Default value is 0. Defaults to None.

        Returns:
            Table

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
