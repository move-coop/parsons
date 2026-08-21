"""Tests for the Shopify connector."""

from parsons import Table
from test.conftest import assert_matching_tables

MOCK_ORDERS_ALL = {
    "orders": [
        {"created_at": "2020-10-19T12:00:00-04:00", "financial_status": "paid", "id": 1},
        {"created_at": "2020-10-20T12:00:00-04:00", "financial_status": "refunded", "id": 2},
    ]
}
MOCK_ORDERS_COMPLETED = {
    "orders": [{"created_at": "2020-10-19T12:00:00-04:00", "financial_status": "paid", "id": 1}]
}
MOCK_ORDERS_DATE = {
    "orders": [{"created_at": "2020-10-20T12:00:00-04:00", "financial_status": "refunded", "id": 2}]
}
MOCK_RESULT_ALL = Table(
    [
        ("created_at", "financial_status", "id"),
        ("2020-10-19T12:00:00-04:00", "paid", 1),
        ("2020-10-20T12:00:00-04:00", "refunded", 2),
    ]
)
MOCK_RESULT_COMPLETED = Table(
    [("created_at", "financial_status", "id"), ("2020-10-19T12:00:00-04:00", "paid", 1)]
)
MOCK_RESULT_DATE = Table(
    [("created_at", "financial_status", "id"), ("2020-10-20T12:00:00-04:00", "refunded", 2)]
)


def test_get_count(shopify, requests_mock):
    requests_mock.get(shopify.get_query_url(None, None, "orders", True), json={"count": 2})
    requests_mock.get(shopify.get_query_url("2020-10-20", None, "orders", True), json={"count": 1})
    requests_mock.get(shopify.get_query_url(None, 2, "orders", True), json={"count": 1})

    assert shopify.get_count(None, None, "orders") == 2
    assert shopify.get_count("2020-10-20", None, "orders") == 1
    assert shopify.get_count(None, 2, "orders") == 1


def test_get_orders(shopify, requests_mock):
    requests_mock.get(shopify.get_query_url(None, None, "orders", False), json=MOCK_ORDERS_ALL)
    requests_mock.get(
        shopify.get_query_url("2020-10-20", None, "orders", False), json=MOCK_ORDERS_DATE
    )
    requests_mock.get(shopify.get_query_url(None, 2, "orders", False), json=MOCK_ORDERS_DATE)
    requests_mock.get(
        shopify.get_query_url(None, None, "orders", False) + "&financial_status=paid",
        json=MOCK_ORDERS_COMPLETED,
    )

    assert_matching_tables(shopify.get_orders(None, None, False), MOCK_RESULT_ALL)
    assert_matching_tables(shopify.get_orders("2020-10-20", None, False), MOCK_RESULT_DATE)
    assert_matching_tables(shopify.get_orders(None, 2, False), MOCK_RESULT_DATE)
    assert_matching_tables(shopify.get_orders(None, None, True), MOCK_RESULT_COMPLETED)


def test_get_query_url(shopify, subdomain, api_version):
    base = f"https://{subdomain}.myshopify.com/admin/api/{api_version}"

    assert (
        shopify.get_query_url(None, None, "orders", True)
        == f"{base}/orders/count.json?limit=250&status=any"
    )
    assert (
        shopify.get_query_url("2020-10-20", None, "orders", True)
        == f"{base}/orders/count.json?limit=250&status=any"
        "&created_at_min=2020-10-20T00:00:00&created_at_max=2020-10-21T00:00:00"
    )
    assert (
        shopify.get_query_url(None, 2, "orders", True)
        == f"{base}/orders/count.json?limit=250&status=any&since_id=2"
    )
    assert (
        shopify.get_query_url(None, None, "orders", False)
        == f"{base}/orders.json?limit=250&status=any"
    )


def test_graphql(shopify, subdomain, api_version, requests_mock):
    mock_graphql = {"data": {"orders": {"edges": [{"node": {"id": 1}}]}}}
    requests_mock.post(
        f"https://{subdomain}.myshopify.com/admin/api/{api_version}/graphql.json",
        json=mock_graphql,
    )

    result = shopify.graphql(
        '{ orders(query: "financial_status:=paid", first: 100) { edges { node { id } } } }'
    )

    assert result == mock_graphql["data"]
