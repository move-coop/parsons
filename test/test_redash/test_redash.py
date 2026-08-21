"""Tests for the Redash connector."""

import pytest

from parsons import Redash, Table
from parsons.redash.redash import RedashTimeout
from test.conftest import assert_matching_tables

API_KEY = "abc123"
MOCK_CSV = "foo,bar\n1,2\n3,4"
MOCK_RESULT = Table([("foo", "bar"), ("1", "2"), ("3", "4")])
MOCK_DATA_SOURCE = {
    "id": 1,
    "name": "Data Source 1",
    "type": "redshift",
    "options": {
        "dbname": "db_name",
        "host": "host.example.com",
        "password": "--------",
        "port": 5439,
        "user": "username",
    },
}


def test_get_data_source(redash, base_url, requests_mock):
    requests_mock.get(f"{base_url}/api/data_sources/1", json=MOCK_DATA_SOURCE)

    assert redash.get_data_source(1) == MOCK_DATA_SOURCE


def test_update_data_source(redash, base_url, requests_mock):
    requests_mock.post(f"{base_url}/api/data_sources/1", json=MOCK_DATA_SOURCE)

    redash.update_data_source(
        1, "Data Source 1", "redshift", "db_name", "host.example.com", "password", 5439, "username"
    )

    assert requests_mock.call_count == 1


def test_cached_query(base_url, requests_mock):
    requests_mock.get(f"{base_url}/api/queries/5/results.csv", text=MOCK_CSV)

    # An api key passed to the method is sent as a query param...
    redash_no_key = Redash(base_url)
    assert_matching_tables(redash_no_key.get_cached_query_results(5, API_KEY), MOCK_RESULT)
    assert requests_mock.last_request.path == "/api/queries/5/results.csv"
    assert requests_mock.last_request.query == "api_key=abc123"

    # ...whereas a connector-level key uses the header, so no query param.
    redash_with_key = Redash(base_url, API_KEY)
    assert_matching_tables(redash_with_key.get_cached_query_results(5), MOCK_RESULT)
    assert requests_mock.last_request.query == ""


def test_refresh_query(redash, base_url, requests_mock):
    requests_mock.post(
        f"{base_url}/api/queries/5/refresh",
        json={"job": {"status": 3, "query_result_id": 21}},
    )
    requests_mock.get(f"{base_url}/api/queries/5/results/21.csv", text=MOCK_CSV)

    assert_matching_tables(redash.get_fresh_query_results(5, {"yyy": "xxx"}), MOCK_RESULT)


def test_refresh_query_poll(redash, base_url, requests_mock):
    requests_mock.post(f"{base_url}/api/queries/5/refresh", json={"job": {"id": 66, "status": 1}})
    requests_mock.get(
        f"{base_url}/api/jobs/66",
        json={"job": {"id": 66, "status": 3, "query_result_id": 21}},
    )
    requests_mock.get(f"{base_url}/api/queries/5/results/21.csv", text=MOCK_CSV)

    redash.pause = 0.01  # shorten the poll interval
    assert_matching_tables(redash.get_fresh_query_results(5, {"yyy": "xxx"}), MOCK_RESULT)


def test_refresh_query_poll_timeout(redash, base_url, requests_mock):
    requests_mock.post(f"{base_url}/api/queries/5/refresh", json={"job": {"id": 66, "status": 1}})
    requests_mock.get(f"{base_url}/api/jobs/66", json={"job": {"id": 66, "status": 1}})
    requests_mock.get(f"{base_url}/api/queries/5/results/21.csv", text=MOCK_CSV)

    redash.pause = 0.01
    redash.timeout = 0.01
    with pytest.raises(RedashTimeout):
        redash.get_fresh_query_results(5, {"yyy": "xxx"})


def test_load_to_table(redash, base_url, requests_mock):
    requests_mock.post(
        f"{base_url}/api/queries/5/refresh",
        json={"job": {"status": 3, "query_result_id": 21}},
    )
    requests_mock.get(f"{base_url}/api/queries/5/results/21.csv", text=MOCK_CSV)

    table_data = Redash.load_to_table(
        base_url=base_url, user_api_key=API_KEY, query_id=5, params={"x": "y"}, verify=False
    )

    assert_matching_tables(table_data, MOCK_RESULT)


def test_load_to_table_from_env_vars(redash, base_url, requests_mock, monkeypatch):
    monkeypatch.setenv("REDASH_BASE_URL", base_url)
    monkeypatch.setenv("REDASH_USER_API_KEY", API_KEY)
    monkeypatch.setenv("REDASH_QUERY_ID", "5")
    monkeypatch.setenv("REDASH_QUERY_PARAMS", "p_x=y")
    requests_mock.post(
        f"{base_url}/api/queries/5/refresh",
        json={"job": {"status": 3, "query_result_id": 21}},
    )
    requests_mock.get(f"{base_url}/api/queries/5/results/21.csv", text=MOCK_CSV)

    assert_matching_tables(Redash.load_to_table(), MOCK_RESULT)
