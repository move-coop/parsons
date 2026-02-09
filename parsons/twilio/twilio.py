import logging
from typing import Literal

from twilio.rest import Client

from parsons import Table
from parsons.utilities import check_env, json_format

logger = logging.getLogger(__name__)


class Twilio:
    """
    Instantiate the Twilio class.

    Args:
        account_sid (str, optional): The Twilio account sid. Not required if ``TWILIO_ACCOUNT_SID`` env variable is
            passed. Defaults to None.
        auth_token (str, optional): The Twilio auth token. Not required if ``TWILIO_AUTH_TOKEN`` env variable is
            passed. Defaults to None.

    Returns:
        Twilio class

    """

    def __init__(self, account_sid: str | None = None, auth_token: str | None = None):
        self.account_sid = check_env.check("TWILIO_ACCOUNT_SID", account_sid)
        self.auth_token = check_env.check("TWILIO_AUTH_TOKEN", auth_token)
        self.client = Client(self.account_sid, self.auth_token)

    @staticmethod
    def _table_convert(obj):
        tbl = Table([x.__dict__["_properties"] for x in obj])

        if "subresource_uris" in tbl.columns and "uri" in tbl.columns:
            tbl.remove_column("subresource_uris", "uri")

        return tbl

    def get_account(self, account_sid: str) -> dict:
        """
        Get Twilio account.

        Args:
            account_sid (str): The Twilio account sid.

        Returns:
            dict

        """
        r = self.client.api.accounts(account_sid)
        logger.info(f"Retrieved {account_sid} account.")
        return r.__dict__

    def get_accounts(
        self, name: str = None, status: Literal["active", "closed", "supended"] | None = None
    ) -> Table:
        """
        Get Twilio accounts including subaccounts.

        Args:
            name (str, optional): Filter by name of the account. Defaults to None.
            status (Literal["active", "closed", "supended"], optional): Filter by account status.
                Defaults to None.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        r = self.client.api.accounts.list(friendly_name=name, status=status)
        tbl = self._table_convert(r)

        logger.info(f"Retrieved {tbl.num_rows} accounts.")
        return tbl

    def get_account_usage(
        self,
        category: str = None,
        start_date: str = None,
        end_date: str = None,
        time_period: Literal["today", "yesterday", "this_month", "last_month"] | None = None,
        group_by: Literal["daily", "monthly", "yearly"] | None = None,
        exclude_null: bool = False,
    ):
        """
        Get Twilio account usage.

        Args:
            category (str, optional): Filter to a specific type of usage category. The list of possibilities can be
                found
                `here
                <https://www.twilio.com/docs/usage/api/usage-record?code-sample=code-last-months-usage-for-all-usage-categories-4&code-language=Python&code-sdk-version=5.x#usage-all-categories>`_.
                Defaults to None.
            start_date (str, optional): Filter to usage from a specific start date (ex.
                ``2019-01-01``). Defaults to None.
            end_date (str, optional): Filter to usage from a specific end date (ex. ``2019-01-01``).
                Defaults to None.
            time_period (Literal["today", "yesterday", "this_month", "last_month"], optional): A convenience method to filter usage. Defaults to None.
            group_by (Literal["daily", "monthly", "yearly"], optional): The time interval to group usage by. Defaults to None.
            exclude_null (bool, optional): Exclude rows that have no usage. Defaults to False.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        if time_period and group_by:
            raise ValueError("Choose either time_period or group_by, not both.")

        # Add populated arguments
        args = {"category": category, "start_date": start_date, "end_date": end_date}
        args = json_format.remove_empty_keys(args)

        target = time_period or group_by
        resource = getattr(self.client.usage.records, str(target), self.client.usage.records)
        tbl = self._table_convert(resource.list(**args))

        if exclude_null:
            tbl.remove_null_rows("count", null_value="0")

        return tbl

    def get_messages(
        self,
        to=None,
        from_=None,
        date_sent=None,
        date_sent_before=None,
        date_sent_after=None,
    ):
        """
        Get Twilio messages.

        Args:
            to (str, optional): Filter to messages only sent to the specified phone number.
                Defaults to None.
            from_ (str, optional): Filter to messages only sent from the specified phone number.
                Defaults to None.
            date_sent (str, optional): Filter to messages only sent on the specified date (ex.
                ``2019-01-01``). Defaults to None.
            date_sent_before (str, optional): Filter to messages only sent before the specified date (ex.
                ``2019-01-01``). Defaults to None.
            date_sent_after (str, optional): Filter to messages only sent after the specified date (ex.
                ``2019-01-01``). Defaults to None.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        r = self.client.messages.list(
            to=to,
            from_=from_,
            date_sent=date_sent,
            date_sent_before=date_sent_before,
            date_sent_after=date_sent_after,
        )

        tbl = self._table_convert(r)
        logger.info(f"Retrieved {tbl.num_rows} messages.")
        return tbl
