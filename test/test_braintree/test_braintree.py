"""Tests for the Braintree connector.

Braintree wraps the ``braintree`` SDK, which issues its requests through the
``requests`` library — so these tests mock at the HTTP layer with the
``requests_mock`` fixture, returning the gateway's XML payloads.
"""

import datetime
import decimal

from parsons import Table
from test.conftest import assert_matching_tables

IDS_RESPONSE = """
   <search-results>
      <page-size type="integer">50</page-size>
      <ids type="array"><item>{a}</item> <item>{b}</item> </ids>
   </search-results>
"""


def test_dispute_search(braintree, merchant_url, requests_mock, xml):
    requests_mock.post(
        f"{merchant_url}/disputes/advanced_search?page=1", text=xml("dispute_example")
    )

    table = braintree.get_disputes(start_date="2020-01-01", end_date="2020-01-02")

    assert len(table.table) == 3
    assert table[0]["id"] == "abcd1234abcd1234"
    assert table[1]["id"] == "ghjk6789ghjk6789"
    assert table[0]["transaction_id"] == "d9f876fg"
    assert table[1]["transaction_id"] == "98df87fg"
    assert table[0]["reason"] == "transaction_amount_differs"
    assert table[1]["reason"] == "fraud"


def test_transaction_search_just_ids(braintree, merchant_url, requests_mock):
    requests_mock.post(
        f"{merchant_url}/transactions/advanced_search_ids",
        text=IDS_RESPONSE.format(a="1234abcd", b="0987asdf"),
    )

    table = braintree.get_transactions(
        disbursement_start_date="2020-01-01",
        disbursement_end_date="2020-01-02",
        just_ids=True,
    )

    assert_matching_tables(table, Table([["id"], ["1234abcd"], ["0987asdf"]]))
    assert len(table[0].keys()) == 1


def test_transaction_search_full(braintree, merchant_url, requests_mock, xml):
    ids = Table([["id"], ["1234abcd"], ["0987asdf"]])
    requests_mock.post(
        f"{merchant_url}/transactions/advanced_search", text=xml("transaction_example")
    )

    full_table = braintree.get_transactions(
        disbursement_start_date="2020-01-01",
        disbursement_end_date="2020-01-02",
        table_of_ids=ids,
    )

    assert len(full_table.table) == 3
    assert len(full_table[0].keys()) == 67
    assert full_table[0]["disbursement_date"] == datetime.date(2019, 12, 30)
    assert full_table[0]["credit_card_bin"] == "789234"
    assert full_table[0]["disbursement_success"]
    assert full_table[0]["amount"] == decimal.Decimal("150.00")


def test_subscription_search_just_ids(braintree, merchant_url, requests_mock):
    requests_mock.post(
        f"{merchant_url}/subscriptions/advanced_search_ids",
        text=IDS_RESPONSE.format(a="aabbcc", b="1a2b3c"),
    )

    table = braintree.get_subscriptions(
        start_date="2022-08-22", end_date="2022-08-23", just_ids=True
    )

    assert_matching_tables(table, Table([["id"], ["aabbcc"], ["1a2b3c"]]))
    assert len(table[0].keys()) == 1


def test_subscription_search_full(braintree, merchant_url, requests_mock, xml):
    ids = Table([["id"], ["aabbcc"], ["1a2b3c"]])
    requests_mock.post(
        f"{merchant_url}/subscriptions/advanced_search", text=xml("subscription_example")
    )

    full_table = braintree.get_subscriptions(
        start_date="2020-01-01",
        end_date="2020-01-02",
        table_of_ids=ids,
        include_transactions=True,
    )

    assert len(full_table.table) == 3
    assert len(full_table[0].keys()) == 33
    assert full_table[0]["first_billing_date"] == datetime.date(2022, 8, 22)
    assert full_table[0]["transactions"][0].credit_card_details.bin == "999"
    assert full_table[0]["never_expires"]
    assert full_table[0]["price"] == decimal.Decimal("10.00")


def test_query_generation_between(braintree):
    query = braintree._get_query_objects(
        "transaction", **{"disbursement_date": {"between": ["2020-01-01", "2020-01-01"]}}
    )

    assert query[0].name == "disbursement_date"
    assert query[0].to_param() == {"min": "2020-01-01", "max": "2020-01-01"}


def test_query_generation_in_list(braintree):
    query = braintree._get_query_objects(
        "transaction", **{"merchant_account_id": {"in_list": ["abc123"]}}
    )

    assert query[0].name == "merchant_account_id"
    assert query[0].to_param() == ["abc123"]


def test_query_generation_multiple(braintree):
    query = braintree._get_query_objects(
        "dispute",
        **{
            "merchant_account_id": {"in_list": ["abc123"]},
            "effective_date": {"between": ["2020-01-01", "2020-01-01"]},
        },
    )

    assert query[0].name == "merchant_account_id"
    assert query[1].name == "effective_date"
    assert query[1].to_param() == {"min": "2020-01-01", "max": "2020-01-01"}
