import datetime
import decimal
import os
import unittest
import requests_mock
from test.utils import assert_matching_tables

from parsons import Table, Braintree

_dir = os.path.dirname(__file__)


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
            text=open(f"{_dir}/test_data/dispute_example.xml").read(),
        )
        table = self.braintree.get_disputes(start_date="2020-01-01", end_date="2020-01-02")

        self.assertEqual(len(table.table), 3)
        self.assertEqual(table[0]["id"], "abcd1234abcd1234")
        self.assertEqual(table[1]["id"], "ghjk6789ghjk6789")
        self.assertEqual(table[0]["transaction_id"], "d9f876fg")
        self.assertEqual(table[1]["transaction_id"], "98df87fg")
        self.assertEqual(table[0]["reason"], "transaction_amount_differs")
        self.assertEqual(table[1]["reason"], "fraud")

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
            text=open(f"{_dir}/test_data/transaction_example.xml").read(),
        )
        full_table = self.braintree.get_transactions(
            disbursement_start_date="2020-01-01",
            disbursement_end_date="2020-01-02",
            table_of_ids=table,
        )
        self.assertEqual(len(table.table), 3)
        self.assertEqual(len(full_table.table), 3)
        self.assertEqual(table[0]["id"], "1234abcd")
        self.assertEqual(table[1]["id"], "0987asdf")
        self.assertEqual(len(table[0].keys()), 1)
        self.assertEqual(len(full_table[0].keys()), 67)

        self.assertEqual(full_table[0]["disbursement_date"], datetime.date(2019, 12, 30))
        self.assertEqual(full_table[0]["credit_card_bin"], "789234")
        self.assertEqual(full_table[0]["disbursement_success"], True)
        self.assertEqual(full_table[0]["amount"], decimal.Decimal("150.00"))

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
            text=open(f"{_dir}/test_data/subscription_example.xml").read(),
        )
        full_table = self.braintree.get_subscriptions(
            start_date="2020-01-01",
            end_date="2020-01-02",
            table_of_ids=table,
            include_transactions=True,
        )
        self.assertEqual(len(table.table), 3)
        self.assertEqual(len(full_table.table), 3)
        self.assertEqual(table[0]["id"], "aabbcc")
        self.assertEqual(table[1]["id"], "1a2b3c")
        self.assertEqual(len(table[0].keys()), 1)
        self.assertEqual(len(full_table[0].keys()), 33)

        self.assertEqual(full_table[0]["first_billing_date"], datetime.date(2022, 8, 22))
        self.assertEqual(full_table[0]["transactions"][0].credit_card_details.bin, "999")
        self.assertEqual(full_table[0]["never_expires"], True)
        self.assertEqual(full_table[0]["price"], decimal.Decimal("10.00"))

    def test_query_generation(self):
        query = self.braintree._get_query_objects(
            "transaction",
            **{"disbursement_date": {"between": ["2020-01-01", "2020-01-01"]}},
        )
        self.assertEqual(query[0].name, "disbursement_date")
        self.assertEqual(query[0].to_param(), {"min": "2020-01-01", "max": "2020-01-01"})

        query = self.braintree._get_query_objects(
            "transaction", **{"merchant_account_id": {"in_list": ["abc123"]}}
        )

        self.assertEqual(query[0].name, "merchant_account_id")
        self.assertEqual(query[0].to_param(), ["abc123"])

        query = self.braintree._get_query_objects(
            "dispute",
            **{
                "merchant_account_id": {"in_list": ["abc123"]},
                "effective_date": {"between": ["2020-01-01", "2020-01-01"]},
            },
        )
        self.assertEqual(query[0].name, "merchant_account_id")
        self.assertEqual(query[1].name, "effective_date")
        self.assertEqual(query[1].to_param(), {"min": "2020-01-01", "max": "2020-01-01"})
