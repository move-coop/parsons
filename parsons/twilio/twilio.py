import logging
from collections.abc import Iterable
from typing import Literal

from twilio.rest import Client

from parsons import Table
from parsons.utilities import check_env, json_format

logger = logging.getLogger(__name__)


class Twilio:
    """
    Instantiate the Twilio class.

    Args:
        account_sid:
            The Twilio account sid.
            Not required if ``TWILIO_ACCOUNT_SID`` env variable is passed.
        auth_token:
            The Twilio auth token.
            Not required if ``TWILIO_AUTH_TOKEN`` env variable is passed.

    """

    def __init__(self, account_sid: str | None = None, auth_token: str | None = None) -> None:
        self.account_sid: str = check_env.check("TWILIO_ACCOUNT_SID", account_sid)
        self.auth_token: str = check_env.check("TWILIO_AUTH_TOKEN", auth_token)
        self.client = Client(self.account_sid, self.auth_token)

    @staticmethod
    def _table_convert(obj: Iterable) -> Table:
        tbl = Table([x._properties for x in obj])

        if "subresource_uris" in tbl.columns and "uri" in tbl.columns:
            tbl.remove_column("subresource_uris", "uri")

        return tbl

    def get_account(self, account_sid: str) -> dict:
        """
        Get Twilio account.

        Args:
            account_sid: The Twilio account sid

        """
        r = self.client.api.accounts(account_sid)
        logger.info(f"Retrieved {account_sid} account.")
        return r.__dict__

    def get_accounts(self, name: str | None = None, status: str | None = None) -> Table:
        """
        Get Twilio accounts including subaccounts.

        Args:
            name: Filter to name of the account
            status:
                Filter to an account status of ``active``, ``closed`` or ``suspended``.

        """
        r = self.client.api.accounts.list(friendly_name=name, status=status)
        tbl = self._table_convert(r)

        logger.info(f"Retrieved {tbl.num_rows} accounts.")
        return tbl

    def get_account_usage(
        self,
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        time_period: Literal["today", "yesterday", "this_month", "last_month"] | None = None,
        group_by: Literal["daily", "monthly", "yearly"] | None = None,
        exclude_null: bool = False,
    ) -> Table:
        """
        Get Twilio account usage.

        Args:
            category:
                Filter to a specific type of usage category. The list of possibilities can be found
                `here <https://www.twilio.com/docs/usage/api/usage-record#usage-all-categories>`__.
            start_date: Filter to usage from a specific start date (ex. ``2019-01-01``).
            end_date: Filter to usage from a specific end date (ex. ``2019-01-01``).
            time_period:
                A convenience method to filter usage.
                Can be one of ``today``, ``yesterday``, ``this_month``, ``last_month``.
            group_by:
                The time interval to group usage by.
                Can be one of ``daily``, ``monthly`` or ``yearly``.
            exclude_null: Exclude rows that have no usage.

        """
        args = {"category": category, "start_date": start_date, "end_date": end_date}
        args = json_format.remove_empty_keys(args)

        # Parse out the time_periods
        target = time_period or group_by
        if target:
            r = getattr(self.client.usage.records, target).list(**args)
        else:
            r = self.client.usage.records.list(**args)

        tbl = self._table_convert(r)

        if exclude_null:
            tbl.remove_null_rows("count", null_value="0")

        return tbl

    def get_messages(
        self,
        to: str | None = None,
        from_: str | None = None,
        date_sent: str | None = None,
        date_sent_before: str | None = None,
        date_sent_after: str | None = None,
    ) -> Table:
        """
        Get Twilio messages.

        Args:
            to: Filter to messages only sent to the specified phone number.
            `from_`: Filter to messages only sent from the specified phone number.
            date_sent:
                Filter to messages only sent on the specified date (ex. ``2019-01-01``).
            date_sent_before:
                Filter to messages only sent before the specified date (ex. ``2019-01-01``).
            date_sent_after:
                Filter to messages only sent after the specified date (ex. ``2019-01-01``).

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
