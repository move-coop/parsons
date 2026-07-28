"""Tests for the Twilio connector.

Twilio wraps a third-party ``twilio.rest.Client``, so that client is the boundary we
mock (see the ``twilio`` fixture in conftest.py). The connector's own request routing
and table conversion (``_table_convert``) run for real.
"""

import pytest

from parsons import Table
from test.conftest import assert_matching_tables


class FakeRecord:
    """A Twilio resource stand-in exposing the ``_properties`` dict the connector reads."""

    def __init__(self, **properties):
        self._properties = properties


def test_get_account(twilio):
    twilio.get_account("FAKESID")

    twilio.client.api.accounts.assert_called_with("FAKESID")


def test_get_accounts(twilio):
    twilio.get_accounts(name="MyOrg", status="active")

    twilio.client.api.accounts.list.assert_called_with(friendly_name="MyOrg", status="active")


def test_get_accounts_returns_table(twilio):
    twilio.client.api.accounts.list.return_value = [
        FakeRecord(sid="AC1", friendly_name="Org1"),
        FakeRecord(sid="AC2", friendly_name="Org2"),
    ]

    tbl = twilio.get_accounts()

    assert_matching_tables(
        tbl,
        Table(
            [
                {"sid": "AC1", "friendly_name": "Org1"},
                {"sid": "AC2", "friendly_name": "Org2"},
            ]
        ),
    )


def test_get_messages(twilio):
    twilio.get_messages(date_sent="2019-10-29")

    twilio.client.messages.list.assert_called_with(
        date_sent="2019-10-29",
        to=None,
        from_=None,
        date_sent_before=None,
        date_sent_after=None,
    )


def test_table_convert_drops_uri_columns(twilio):
    # When both subresource_uris and uri are present, _table_convert removes them.
    twilio.client.messages.list.return_value = [
        FakeRecord(sid="SM1", body="hi", uri="/x", subresource_uris={"media": "/m"}),
    ]

    tbl = twilio.get_messages()

    assert "uri" not in tbl.columns
    assert "subresource_uris" not in tbl.columns
    assert tbl["sid"] == ["SM1"]
    assert tbl["body"] == ["hi"]


def test_table_convert_keeps_uri_without_subresource_uris(twilio):
    # Only one of the two columns present -> neither is removed (they go together).
    twilio.client.messages.list.return_value = [FakeRecord(sid="SM1", uri="/x")]

    tbl = twilio.get_messages()

    assert "uri" in tbl.columns


@pytest.mark.parametrize("time_period", ["today", "yesterday", "this_month", "last_month"])
def test_get_account_usage_time_period(twilio, time_period):
    twilio.get_account_usage(time_period=time_period)

    getattr(twilio.client.usage.records, time_period).list.assert_called_once()


@pytest.mark.parametrize("group_by", ["daily", "monthly", "yearly"])
def test_get_account_usage_group_by(twilio, group_by):
    twilio.get_account_usage(group_by=group_by, start_date="10-19-2019")

    getattr(twilio.client.usage.records, group_by).list.assert_called_with(start_date="10-19-2019")


def test_get_account_usage_defaults_to_plain_records(twilio):
    # With no time_period or group_by, the plain records.list endpoint is used.
    twilio.get_account_usage()

    twilio.client.usage.records.list.assert_called_once()


def test_get_account_usage_keeps_null_rows_by_default(twilio):
    twilio.client.usage.records.list.return_value = [
        FakeRecord(category="sms", count="5"),
        FakeRecord(category="calls", count="0"),
    ]

    tbl = twilio.get_account_usage()

    assert tbl.num_rows == 2


def test_get_account_usage_exclude_null(twilio):
    twilio.client.usage.records.list.return_value = [
        FakeRecord(category="sms", count="5"),
        FakeRecord(category="calls", count="0"),
    ]

    tbl = twilio.get_account_usage(exclude_null=True)

    assert tbl.num_rows == 1
    assert tbl["category"] == ["sms"]
