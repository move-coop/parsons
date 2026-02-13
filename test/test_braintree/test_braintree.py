import datetime
import decimal
import unittest
from pathlib import Path

import requests_mock

from parsons import Braintree, Table
from test.conftest import assert_matching_tables

_dir = Path(__file__).parent


class TestBraintree(unittest.TestCase):
    def setUp(self):
        self.braintree = Braintree(
            merchant_id="abcd1234abcd1234",
            public_key="abcd1234abcd1234",
            private_key="abcd1234abcd1234abcd1234abcd1234",
        )

    @requests_mock.Mocker()
    def test_dispute_search(self, m):
        m.post(
            "https://api.braintreegateway.com:443"
            "/merchants/abcd1234abcd1234/disputes/advanced_search?page=1",
            text=(Path(_dir) / "test_data/dispute_example.xml").read_text(),
        )
        table = self.braintree.get_disputes(start_date="2020-01-01", end_date="2020-01-02")

        assert len(table.table) == 3
        assert table[0]["id"] == "abcd1234abcd1234"
        assert table[1]["id"] == "ghjk6789ghjk6789"
        assert table[0]["transaction_id"] == "d9f876fg"
        assert table[1]["transaction_id"] == "98df87fg"
        assert table[0]["reason"] == "transaction_amount_differs"
        assert table[1]["reason"] == "fraud"

    @requests_mock.Mocker()
    def test_transaction_search(self, m):
        m.post(
            "https://api.braintreegateway.com:443"
            "/merchants/abcd1234abcd1234/transactions/advanced_search_ids",
            text="""
               <search-results>
                  <page-size type="integer">50</page-size>
                  <ids type="array"><item>1234abcd</item> <item>0987asdf</item> </ids>
               </search-results>
        """,
        )
        table = self.braintree.get_transactions(
            disbursement_start_date="2020-01-01",
            disbursement_end_date="2020-01-02",
            just_ids=True,
        )
        assert_matching_tables(table, Table([["id"], ["1234abcd"], ["0987asdf"]]))
        m.post(
            "https://api.braintreegateway.com:443"
            "/merchants/abcd1234abcd1234/transactions/advanced_search",
            text=(Path(_dir) / "test_data/transaction_example.xml").read_text(),
        )
        full_table = self.braintree.get_transactions(
            disbursement_start_date="2020-01-01",
            disbursement_end_date="2020-01-02",
            table_of_ids=table,
        )
        assert len(table.table) == 3
        assert len(full_table.table) == 3
        assert table[0]["id"] == "1234abcd"
        assert table[1]["id"] == "0987asdf"
        assert len(table[0].keys()) == 1
        assert len(full_table[0].keys()) == 67

        assert full_table[0]["disbursement_date"] == datetime.date(2019, 12, 30)
        assert full_table[0]["credit_card_bin"] == "789234"
        assert full_table[0]["disbursement_success"]
        assert full_table[0]["amount"] == decimal.Decimal("150.00")

    @requests_mock.Mocker()
    def test_subscription_search(self, m):
        m.post(
            "https://api.braintreegateway.com:443"
            "/merchants/abcd1234abcd1234/subscriptions/advanced_search_ids",
            text="""
               <search-results>
                  <page-size type="integer">50</page-size>
                  <ids type="array"><item>aabbcc</item> <item>1a2b3c</item> </ids>
               </search-results>
        """,
        )
        table = self.braintree.get_subscriptions(
            start_date="2022-08-22", end_date="2022-08-23", just_ids=True
        )
        assert_matching_tables(table, Table([["id"], ["aabbcc"], ["1a2b3c"]]))
        m.post(
            "https://api.braintreegateway.com:443"
            "/merchants/abcd1234abcd1234/subscriptions/advanced_search",
            text=(Path(_dir) / "test_data/subscription_example.xml").read_text(),
        )
        full_table = self.braintree.get_subscriptions(
            start_date="2020-01-01",
            end_date="2020-01-02",
            table_of_ids=table,
            include_transactions=True,
        )
        assert len(table.table) == 3
        assert len(full_table.table) == 3
        assert table[0]["id"] == "aabbcc"
        assert table[1]["id"] == "1a2b3c"
        assert len(table[0].keys()) == 1
        assert len(full_table[0].keys()) == 33

        assert full_table[0]["first_billing_date"] == datetime.date(2022, 8, 22)
        assert full_table[0]["transactions"][0].credit_card_details.bin == "999"
        assert full_table[0]["never_expires"]
        assert full_table[0]["price"] == decimal.Decimal("10.00")

    def test_query_generation(self):
        query = self.braintree._get_query_objects(
            "transaction",
            **{"disbursement_date": {"between": ["2020-01-01", "2020-01-01"]}},
        )
        assert query[0].name == "disbursement_date"
        assert query[0].to_param() == {"min": "2020-01-01", "max": "2020-01-01"}

        query = self.braintree._get_query_objects(
            "transaction", **{"merchant_account_id": {"in_list": ["abc123"]}}
        )

        assert query[0].name == "merchant_account_id"
        assert query[0].to_param() == ["abc123"]

        query = self.braintree._get_query_objects(
            "dispute",
            **{
                "merchant_account_id": {"in_list": ["abc123"]},
                "effective_date": {"between": ["2020-01-01", "2020-01-01"]},
            },
        )
        assert query[0].name == "merchant_account_id"
        assert query[1].name == "effective_date"
        assert query[1].to_param() == {"min": "2020-01-01", "max": "2020-01-01"}
