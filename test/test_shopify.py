from parsons import Table, Shopify
from test.utils import assert_matching_tables
import requests_mock
import unittest

SUBDOMAIN = "myorg"
PASSWORD = "abc123"
API_KEY = "abc123"
API_VERSION = "2020-10"


class TestShopify(unittest.TestCase):
    mock_count_all = {"count": 2}
    mock_count_date = mock_count_since = {"count": 1}
    mock_graphql = {"data": {"orders": {"edges": [{"node": {"id": 1}}]}}}
    mock_orders_all = {
        "orders": [
            {
                "created_at": "2020-10-19T12:00:00-04:00",
                "financial_status": "paid",
                "id": 1,
            },
            {
                "created_at": "2020-10-20T12:00:00-04:00",
                "financial_status": "refunded",
                "id": 2,
            },
        ]
    }
    mock_orders_completed = {
        "orders": [
            {
                "created_at": "2020-10-19T12:00:00-04:00",
                "financial_status": "paid",
                "id": 1,
            }
        ]
    }
    mock_orders_date = mock_orders_since = {
        "orders": [
            {
                "created_at": "2020-10-20T12:00:00-04:00",
                "financial_status": "refunded",
                "id": 2,
            }
        ]
    }
    mock_result_all = Table(
        [
            ("created_at", "financial_status", "id"),
            ("2020-10-19T12:00:00-04:00", "paid", 1),
            ("2020-10-20T12:00:00-04:00", "refunded", 2),
        ]
    )
    mock_result_completed = Table(
        [
            ("created_at", "financial_status", "id"),
            ("2020-10-19T12:00:00-04:00", "paid", 1),
        ]
    )
    mock_result_date = mock_result_since = Table(
        [
            ("created_at", "financial_status", "id"),
            ("2020-10-20T12:00:00-04:00", "refunded", 2),
        ]
    )

    def setUp(self):
        self.shopify = Shopify(SUBDOMAIN, PASSWORD, API_KEY, API_VERSION)

    @requests_mock.Mocker()
    def test_get_count(self, m):
        m.get(
            self.shopify.get_query_url(None, None, "orders", True),
            json=self.mock_count_all,
        )
        m.get(
            self.shopify.get_query_url("2020-10-20", None, "orders", True),
            json=self.mock_count_date,
        )
        m.get(
            self.shopify.get_query_url(None, 2, "orders", True),
            json=self.mock_count_since,
        )
        self.assertEqual(self.shopify.get_count(None, None, "orders"), 2)
        self.assertEqual(self.shopify.get_count("2020-10-20", None, "orders"), 1)
        self.assertEqual(self.shopify.get_count(None, 2, "orders"), 1)

    @requests_mock.Mocker()
    def test_get_orders(self, m):
        m.get(
            self.shopify.get_query_url(None, None, "orders", False),
            json=self.mock_orders_all,
        )
        m.get(
            self.shopify.get_query_url("2020-10-20", None, "orders", False),
            json=self.mock_orders_date,
        )
        m.get(
            self.shopify.get_query_url(None, 2, "orders", False),
            json=self.mock_orders_since,
        )
        m.get(
            self.shopify.get_query_url(None, None, "orders", False) + "&financial_status=paid",
            json=self.mock_orders_completed,
        )
        assert_matching_tables(self.shopify.get_orders(None, None, False), self.mock_result_all)
        assert_matching_tables(
            self.shopify.get_orders("2020-10-20", None, False), self.mock_result_date
        )
        assert_matching_tables(self.shopify.get_orders(None, 2, False), self.mock_result_since)
        assert_matching_tables(
            self.shopify.get_orders(None, None, True), self.mock_result_completed
        )

    @requests_mock.Mocker()
    def test_get_query_url(self, m):
        self.assertEqual(
            self.shopify.get_query_url(None, None, "orders", True),
            f"https://{SUBDOMAIN}.myshopify.com/admin/api/{API_VERSION}/orders/"
            + "count.json?limit=250&status=any",
        )
        self.assertEqual(
            self.shopify.get_query_url("2020-10-20", None, "orders", True),
            f"https://{SUBDOMAIN}.myshopify.com/admin/api/{API_VERSION}/orders/"
            + "count.json?limit=250&status=any&created_at_min=2020-10-20T00:00:00&"
            + "created_at_max=2020-10-21T00:00:00",
        )
        self.assertEqual(
            self.shopify.get_query_url(None, 2, "orders", True),
            f"https://{SUBDOMAIN}.myshopify.com/admin/api/{API_VERSION}/orders/"
            + "count.json?limit=250&status=any&since_id=2",
        )
        self.assertEqual(
            self.shopify.get_query_url(None, None, "orders", False),
            f"https://{SUBDOMAIN}.myshopify.com/admin/api/{API_VERSION}/orders.json?"
            + "limit=250&status=any",
        )

    @requests_mock.Mocker()
    def test_graphql(self, m):
        m.post(
            "https://{0}.myshopify.com/admin/api/{1}/graphql.json".format(SUBDOMAIN, API_VERSION),
            json=self.mock_graphql,
        )
        self.assertEqual(
            self.shopify.graphql(
                """
            {{
                orders(query: "financial_status:=paid", first: 100) {{
                    edges {{
                        node {{
                            id
                        }}
                    }}
                }}
            }}
        """
            ),
            self.mock_graphql["data"],
        )
