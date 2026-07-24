"""Tests for the Quickbase connector."""

import json


def _load(shared_datadir, name: str):
    return json.loads((shared_datadir / name).read_text())


def test_get_app_tables(quickbase, requests_mock, shared_datadir):
    requests_mock.get(
        f"{quickbase.api_hostname}/tables?appId=test",
        json=_load(shared_datadir, "get_app_tables.json"),
    )

    tbl = quickbase.get_app_tables(app_id="test")

    assert tbl.num_rows == 2
    assert requests_mock.last_request.qs["appid"] == ["test"]


def test_query_records(quickbase, requests_mock, shared_datadir):
    requests_mock.post(
        f"{quickbase.api_hostname}/records/query",
        json=_load(shared_datadir, "query_records.json"),
    )

    tbl = quickbase.query_records(table_from="test_table")

    assert tbl.num_rows == 1
    assert requests_mock.last_request.json()["from"] == "test_table"


def test_query_records_unwraps_values_and_renames_columns(quickbase, requests_mock, shared_datadir):
    """Numeric field ids become their labels, and each cell is unwrapped from {"value": ...}."""
    requests_mock.post(
        f"{quickbase.api_hostname}/records/query",
        json=_load(shared_datadir, "query_records.json"),
    )

    tbl = quickbase.query_records(table_from="test_table")

    assert set(tbl.columns) == {
        "date created",
        "first name",
        "last name",
        "phone number",
        "address: city",
        "email",
        "zip code",
        "city",
        "state/region",
        "street 1",
        "gender identity",
    }
    row = tbl[0]
    assert row["first name"] == "First name"
    assert row["email"] == "exampleemail@example.com"
    assert row["phone number"] == "(555) 555-5555"
