import logging
import re
from datetime import datetime
from typing import Literal

from requests.auth import HTTPBasicAuth

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.utilities.datetime import convert_date_to_iso

logger = logging.getLogger(__name__)


class Mailchimp:
    """
    Instantiate Mailchimp Class.

    Args:
        api_key:
            The Mailchimp-provided application key.
            Not required if ``MAILCHIMP_API_KEY`` env variable set.

    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key: str = check_env.check("MAILCHIMP_API_KEY", api_key)
        self.domain = re.findall("(?<=-).+$", self.api_key)[0]
        self.uri = f"https://{self.domain}.api.mailchimp.com/3.0/"
        self.client = APIConnector(self.uri, auth=HTTPBasicAuth("x", self.api_key))

    def get_lists(
        self,
        fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        count: int = 10,
        offset: int = 0,
        before_date_created: datetime | str | None = None,
        since_date_created: datetime | str | None = None,
        before_campaign_last_sent: datetime | str | None = None,
        since_campaign_last_sent: datetime | str | None = None,
        email: str | None = None,
        sort_field: Literal["date_created"] | None = None,
        sort_dir: Literal["ASC", "DESC"] | None = None,
    ) -> Table:
        """
        Get a table of lists under the account based on query parameters.

        Note that argument descriptions here are sourced from
        Mailchimp's official API documentation.

        Args:
            fields:
                A list of fields to return.
                Reference parameters of sub-objects with dot notation.
            exclude_fields:
                A list of fields to exclude.
                Reference parameters of sub-objects with dot notation.
            count:
                The number of records to return.
                Maximum value is 1000.
            offset:
                The number of records from a collection to skip.
                Iterating over large collections with this parameter can be slow.
            before_date_created:
                Restrict response to lists created before the set date.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            since_date_created:
                Restrict results to lists created after the set date.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            before_campaign_last_sent:
                Restrict results to lists created before the last campaign send date.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            since_campaign_last_sent:
                Restrict results to lists created after the last campaign send date.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            email:
                Restrict results to lists that include a specific subscriber's email address.
            sort_field: Returns files sorted by the specified field.
            sort_dir: Determines the order direction for sorted results.

        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
            "before_date_created": convert_date_to_iso(before_date_created),
            "since_date_created": convert_date_to_iso(since_date_created),
            "before_campaign_last_sent": convert_date_to_iso(before_campaign_last_sent),
            "since_campaign_last_sent": convert_date_to_iso(since_campaign_last_sent),
            "email": email,
            "sort_field": sort_field,
            "sort_dir": sort_dir,
        }

        response = self.client.get_request(url="lists", params=params)
        tbl = Table(response["lists"])

        logger.info(f"Found {tbl.num_rows} lists.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_campaigns(
        self,
        fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        count: int = 10,
        offset: int = 0,
        type: Literal["regular", "plaintext", "absplit", "rss", "variate"] | None = None,
        status: Literal["save", "paused", "schedule", "sending", "sent"] | None = None,
        before_send_time: datetime | str | None = None,
        since_send_time: datetime | str | None = None,
        before_create_time: datetime | str | None = None,
        since_create_time: datetime | str | None = None,
        list_id: str | None = None,
        folder_id: str | None = None,
        member_id: str | None = None,
        sort_field: Literal["create_time", "send_time"] | None = None,
        sort_dir: Literal["ASC", "DESC"] | None = None,
    ) -> Table:
        """
        Get a table of campaigns under the account based on query parameters.

        Note that argument descriptions here are sourced from
        Mailchimp's official API documentation.

        Args:
            fields:
                A list of fields to return.
                Reference parameters of sub-objects with dot notation.
            exclude_fields:
                A list of fields to exclude.
                Reference parameters of sub-objects with dot notation.
            count:
                The number of records to return.
                Maximum value is 1000.
            offset:
                The number of records from a collection to skip.
                Iterating over large collections with this parameter can be slow.
            type: The campaign type.
            status: The status of the campaign.
            before_send_time:
                Restrict the response to campaigns sent before the set time.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            since_send_time:
                Restrict the response to campaigns sent after the set time.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            before_create_time:
                Restrict the response to campaigns created before the set time.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            since_create_time:
                Restrict the response to campaigns created after the set time.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            list_id: The unique id for the list.
            folder_id: The unique folder id.
            member_id:
                Retrieve campaigns sent to a particular list member.
                Member ID is The MD5 hash of the lowercase version of
                the list member’s email address.
            sort_field: Returns files sorted by the specified field.
            sort_dir: Determines the order direction for sorted results.

        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
            "type": type,
            "status": status,
            "before_send_time": convert_date_to_iso(before_send_time),
            "since_send_time": convert_date_to_iso(since_send_time),
            "before_create_time": convert_date_to_iso(before_create_time),
            "since_create_time": convert_date_to_iso(since_create_time),
            "list_id": list_id,
            "folder_id": folder_id,
            "member_id": member_id,
            "sort_field": sort_field,
            "sort_dir": sort_dir,
        }

        response = self.client.get_request(url="campaigns", params=params)
        tbl = Table(response["campaigns"])

        logger.info(f"Found {tbl.num_rows} campaigns.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_members(
        self,
        list_id: str,
        fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        count: int = 10,
        offset: int = 0,
        email_type: str | None = None,
        status: Literal[
            "subscribed", "unsubscribed", "cleaned", "pending", "transactional", "archived"
        ]
        | None = None,
        since_timestamp_opt: datetime | str | None = None,
        before_timestamp_opt: datetime | str | None = None,
        since_last_changed: datetime | str | None = None,
        before_last_changed: datetime | str | None = None,
        unique_email_id: str | None = None,
        vip_only: bool = False,
        interest_category_id: str | None = None,
        interest_ids: list[str] | None = None,
        interest_match: Literal["any", "all", "none"] | None = None,
        sort_field: Literal["timestamp_opt", "timestamp_signup", "last_changed"] | None = None,
        sort_dir: Literal["ASC", "DESC"] | None = None,
        since_last_campaign: datetime | str | None = None,
        unsubscribed_since: datetime | str | None = None,
    ) -> Table:
        """
        Get a table of members in a list based on query parameters.

        Note that argument descriptions here are sourced from
        Mailchimp's official API documentation.

        Args:
            list_id: The unique ID of the list to fetch members from.
            fields:
                A list of fields to return.
                Reference parameters of sub-objects with dot notation.
            exclude_fields:
                A list of fields to exclude.
                Reference parameters of sub-objects with dot notation.
            count:
                The number of records to return.
                Maximum value is 1000.
            offset:
                The number of records from a collection to skip.
                Iterating over large collections with this parameter can be slow.
            email_type: The email type.
            status: The subscriber's status.
            since_timestamp_opt:
                Restrict results to subscribers who opted-in after the set timeframe.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            before_timestamp_opt:
                Restrict results to subscribers who opted-in before the set timeframe.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            since_last_changed:
                Restrict results to subscribers whose
                information changed after the set timeframe.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            before_last_changed:
                Restrict results to subscribers whose
                information changed before the set timeframe.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.
            unique_email_id:
                A unique identifier for the email address across all Mailchimp lists.
                This parameter can be found in any links with Ecommerce Tracking enabled.
            vip_only:
                A filter to return only the list's VIP members.
                Passing true will restrict results to VIP list members,
                passing false will return all list members.
            interest_category_id: The unique id for the interest category.
            interest_ids:
                A list of interest ids present for any supplied interest categories.
                Used to filter list members by interests.
                Must be accompanied by `interest_category_id` and `interest_match`.
            interest_match:
                Used to filter list members by interests.
                Must be accompanied by `interest_category_id` and `interest_ids`.
                ``any`` will match a member with any of the interest supplied.
                ``all`` will only match members with every interest supplied.
                ``None`` will match members without any of the interest supplied.
            sort_field: Returns files sorted by the specified field.
            sort_dir: Determines the order direction for sorted results.
            since_last_campaign:
                Filter subscribers by those
                ``subscribed``/``unsubscribed``/``pending``/``cleaned``
                since last email campaign send.
                Member `status` is required to use this filter.
            unsubscribed_since:
                Filter subscribers by those unsubscribed since a specific date.
                Using any `status` other than ``unsubscribed``
                with this filter will result in an error.

        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
            "email_type": email_type,
            "status": status,
            "since_timestamp_opt": convert_date_to_iso(since_timestamp_opt),
            "before_timestamp_opt": convert_date_to_iso(before_timestamp_opt),
            "since_last_changed": convert_date_to_iso(since_last_changed),
            "before_last_changed": convert_date_to_iso(before_last_changed),
            "unqiue_email_id": unique_email_id,
            "vip_only": vip_only,
            "interest_category_id": interest_category_id,
            "interest_ids": interest_ids,
            "interest_match": interest_match,
            "sort_field": sort_field,
            "sort_dir": sort_dir,
            "since_last_campaign": convert_date_to_iso(since_last_campaign),
            "unsubscribed_since": convert_date_to_iso(unsubscribed_since),
        }

        response = self.client.get_request(url=f"lists/{list_id}/members", params=params)
        tbl = Table(response["members"])

        logger.info(f"Found {tbl.num_rows} members.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_campaign_emails(
        self,
        campaign_id: str,
        fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        count: int = 10,
        offset: int = 0,
        since: datetime | str | None = None,
    ) -> Table:
        """
        Get a table of individual emails from a campaign based on query parameters.

        Note that argument descriptions here are sourced from
        Mailchimp's official API documentation.

        Args:
            campaign_id: The unique ID of the campaign to fetch emails from.
            fields:
                A list of fields to return.
                Reference parameters of sub-objects with dot notation.
            exclude_fields:
                A list of fields to exclude.
                Reference parameters of sub-objects with dot notation.
            count:
                The number of records to return.
                Maximum value is 1000.
            offset:
                The number of records from a collection to skip.
                Iterating over large collections with this parameter can be slow.
            since:
                Restrict results to email activity events that occur after a specific time.
                We recommend ISO 8601 time format: ``2015-10-21T15:41:36+00:00``.

        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
            "since": convert_date_to_iso(since),
        }

        response = self.client.get_request(
            url=f"reports/{campaign_id}/email-activity", params=params
        )
        tbl = Table(response["emails"])

        logger.info(f"Found {tbl.num_rows} emails for campaign {campaign_id}.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_unsubscribes(
        self,
        campaign_id: str,
        fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        count: int = 10,
        offset: int = 0,
    ) -> Table:
        """
        Get a table of unsubscribes associated with a campaign based on query parameters.

        Note that argument descriptions here are sourced from
        Mailchimp's official API documentation.

        Args:
            campaign_id:
                The unique ID of the campaign to fetch unsubscribes from.
            fields:
                A list of fields to return.
                Reference parameters of sub-objects with dot notation.
            exclude_fields:
                A list of fields to exclude.
                Reference parameters of sub-objects with dot notation.
            count:
                The number of records to return.
                Maximum value is 1000.
            offset:
                The number of records from a collection to skip.
                Iterating over large collections with this parameter can be slow.

        """
        params = {
            "fields": fields,
            "exclude_fields": exclude_fields,
            "count": count,
            "offset": offset,
        }

        response = self.client.get_request(url=f"reports/{campaign_id}/unsubscribed", params=params)
        tbl = Table(response["unsubscribes"])

        logger.info(f"Found {tbl.num_rows} unsubscribes for {campaign_id}.")
        return tbl if tbl.num_rows > 0 else Table()
