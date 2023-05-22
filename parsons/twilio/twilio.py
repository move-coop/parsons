from twilio.rest import Client
from parsons.utilities import check_env, json_format
from parsons.etl import Table
import logging


logger = logging.getLogger(__name__)


class Twilio:
    """
    Instantiate the Twilio class

    `Args:`
        account_sid: str
            The Twilio account sid. Not required if ``TWILIO_ACCOUNT_SID`` env variable is
            passed.
        auth_token: str
            The Twilio auth token. Not required if ``TWILIO_AUTH_TOKEN`` env variable is
            passed.
    `Returns`:
        Twilio class
    """

    def __init__(self, account_sid=None, auth_token=None):

        self.account_sid = check_env.check("TWILIO_ACCOUNT_SID", account_sid)
        self.auth_token = check_env.check("TWILIO_AUTH_TOKEN", auth_token)
        self.client = Client(self.account_sid, self.auth_token)

    def _table_convert(self, obj):
        tbl = Table([x.__dict__["_properties"] for x in obj])

        if "subresource_uris" in tbl.columns and "uri" in tbl.columns:
            tbl.remove_column("subresource_uris", "uri")

        return tbl

    def get_account(self, account_sid):
        """
        Get Twilio account

        `Args:`
            account_sid: str
                The Twilio account sid
        `Returns:`
            dict
        """

        r = self.client.api.accounts(account_sid)
        logger.info(f"Retrieved {account_sid} account.")
        return r.__dict__

    def get_accounts(self, name=None, status=None):
        """
        Get Twilio accounts including subaccounts.

        `Args:`
            name: str
                Filter to name of the account
            status: str
                Filter to an account status of ``active``, ``closed`` or ``suspended``.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self.client.api.accounts.list(friendly_name=name, status=status)
        tbl = self._table_convert(r)

        logger.info(f"Retrieved {tbl.num_rows} accounts.")
        return tbl

    def get_account_usage(
        self,
        category=None,
        start_date=None,
        end_date=None,
        time_period=None,
        group_by=None,
        exclude_null=False,
    ):
        """
        Get Twilio account usage.

        `Args:`
            category: str
                Filter to a specific type of usage category. The list of possibilities can be found
                `here <https://www.twilio.com/docs/usage/api/usage-record?code-sample=code-last-months-usage-for-all-usage-categories-4&code-language=Python&code-sdk-version=5.x#usage-all-categories>`_.
            start_date: str
                Filter to usage from a specific start date (ex. ``2019-01-01``).
            end_date: str
                Filter to usage from a specific end date (ex. ``2019-01-01``).
            time_period: str
                A convenience method to filter usage. Can be one of ``today``, ``yesterday``,
                ``this_month``, ``last_month``.
            group_by: str
                The time interval to group usage by. Can be one of ``daily``, ``monthly`` or
                ``yearly``.
            exclude_null: boolean
                Exclude rows that have no usage.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """  # noqa: E501,E261

        # Add populated arguments
        args = {"category": category, "start_date": start_date, "end_date": end_date}
        args = json_format.remove_empty_keys(args)

        # Parse out the time_periods
        if time_period == "today":
            r = self.client.usage.records.today.list(**args)
        elif time_period == "yesterday":
            r = self.client.usage.records.yesterday.list(**args)
        elif time_period == "this_month":
            r = self.client.usage.records.this_month.list(**args)
        elif time_period == "last_month":
            r = self.client.usage.records.last_month.list(**args)

        # Parse out the group by
        elif group_by == "daily":
            r = self.client.usage.records.daily.list(**args)
        elif group_by == "monthly":
            r = self.client.usage.records.monthly.list(**args)
        elif group_by == "yearly":
            r = self.client.usage.records.yearly.list(**args)
        else:
            r = self.client.usage.records.list(**args)

        tbl = self._table_convert(r)

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

        `Args:`
            to: str
                Filter to messages only sent to the specified phone number.
            from_: str
                Filter to messages only sent from the specified phone number.
            date_sent: str
                Filter to messages only sent on the specified date (ex. ``2019-01-01``).
            date_sent_before: str
                Filter to messages only sent before the specified date (ex. ``2019-01-01``).
            date_sent_after: str
                Filter to messages only sent after the specified date (ex. ``2019-01-01``).
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
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
