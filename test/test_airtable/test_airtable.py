"""Tests for the Airtable connector.

Reference example of the HTTP/REST testing pattern (see docs/contrib_docs/write_tests.rst):
pytest-native functions, the ``requests_mock`` fixture for the HTTP boundary, and
canned response payloads loaded from ``data/`` via the ``load`` fixture.
"""

from parsons import Table
from test.conftest import assert_matching_tables


def test_get_record(airtable, base_uri, requests_mock):
    record_id = "recObtmLUrD5dOnmD"
    response = {
        "id": record_id,
        "fields": {},
        "createdTime": "2019-05-08T19:37:58.000Z",
    }
    requests_mock.get(f"{base_uri}/{record_id}", json=response)

    assert airtable.get_record(record_id) == response


def test_get_records(airtable, base_uri, requests_mock, load):
    requests_mock.get(base_uri, json=load("records_response"))

    expected = Table(
        [
            {
                "id": "recaBMSHTgXREa5ef",
                "createdTime": "2019-05-08T19:37:58.000Z",
                "Name": "This is a row!",
            },
            {
                "id": "recObtmLUrD5dOnmD",
                "createdTime": "2019-05-08T19:37:58.000Z",
                "Name": None,
            },
            {
                "id": "recmeBNnj4cuHPOSI",
                "createdTime": "2019-05-08T19:37:58.000Z",
                "Name": None,
            },
        ]
    )

    assert_matching_tables(airtable.get_records(), expected)


def test_get_records_with_1_sample(airtable, base_uri, requests_mock, load):
    requests_mock.get(base_uri, json=load("records_response_with_more_columns"))

    res = airtable.get_records(sample_size=1)

    assert res.columns == ["id", "createdTime", "Name"]


def test_get_records_with_5_sample(airtable, base_uri, requests_mock, load):
    requests_mock.get(base_uri, json=load("records_response_with_more_columns"))

    res = airtable.get_records(sample_size=5)

    assert res.columns == ["id", "createdTime", "Name", "SecondColumn"]


def test_get_records_with_explicit_headers(airtable, base_uri, requests_mock, load):
    requests_mock.get(base_uri, json=load("records_response_with_more_columns"))

    res = airtable.get_records(["Name", "SecondColumn"], sample_size=1)

    assert res.columns == ["id", "createdTime", "Name", "SecondColumn"]


def test_get_records_with_single_field(airtable, base_uri, requests_mock, load):
    requests_mock.get(base_uri, json=load("records_response_with_more_columns"))

    res = airtable.get_records("Name", sample_size=1)

    assert res.columns == ["id", "createdTime", "Name"]


def test_insert_record(airtable, base_uri, requests_mock, load):
    insert_response = load("insert_response")
    requests_mock.post(base_uri, json=insert_response)

    assert airtable.insert_record({"Name": "Another row!"}) == insert_response


def test_insert_records(airtable, base_uri, requests_mock, load):
    requests_mock.post(base_uri, json=load("insert_responses"))

    resp = airtable.insert_records(Table([{"Name": "Another row!"}, {"Name": "Another!"}]))

    assert len(resp) == 2


def test_update_record(airtable, base_uri, requests_mock):
    record_id = "recObtmLUrD5dOnmD"
    update_response = {
        "id": record_id,
        "fields": {"Name": "AName"},
        "createdTime": "2023-05-22T21:24:15.333134Z",
    }
    requests_mock.patch(f"{base_uri}/{record_id}", json=update_response)

    assert airtable.update_record(record_id, {"Name": "AName"}) == update_response


def test_update_records(airtable, base_uri, requests_mock, load):
    update_responses = load("update_responses")
    requests_mock.patch(base_uri, json=update_responses)

    resp = airtable.update_records(
        Table(
            [
                {"id": "recaBMSHTgXREa5ef", "Name": "Updated Name1"},
                {"id": "recObtmLUrD5dOnmD", "Name": "Updated Name2"},
                {"id": "recmeBNnj4cuHPOSI", "Name": "Updated Name3"},
            ]
        )
    )

    assert len(resp) == len(update_responses["records"])


def test_upsert_records_with_id(airtable, base_uri, requests_mock, load):
    requests_mock.patch(base_uri, json=load("upsert_with_id_responses"))

    resp = airtable.upsert_records(
        Table(
            [
                {"id": "recz9W2ojGNwMdN2y", "Name": "Updated Name1"},
                {"id": "recB5njCET7AvHBbg", "Name": "Updated Name2"},
                {"id": "recz9W2ojgPwMdN2y", "Name": "New Name3"},
            ]
        )
    )

    assert len(resp["records"]) == 3
    assert len(resp["updated_records"]) == 2
    assert len(resp["created_records"]) == 1


def test_upsert_records_with_key(airtable, base_uri, requests_mock, load):
    requests_mock.patch(base_uri, json=load("upsert_with_key_responses"))

    resp = airtable.upsert_records(
        Table(
            [
                {"key": "1", "Name": "New Name1"},
                {"key": "2", "Name": "New Name2"},
                {"key": "3", "Name": "Updated Name3"},
            ]
        ),
        key_fields=["key"],
    )

    assert len(resp["records"]) == 3
    assert len(resp["updated_records"]) == 1
    assert len(resp["created_records"]) == 2


def test_delete_record(airtable, base_uri, requests_mock):
    record_id = "recObtmLUrD5dOnmD"
    response = {"id": record_id, "deleted": True}
    requests_mock.delete(f"{base_uri}/{record_id}", json=response)

    assert airtable.delete_record(record_id) == response


def test_delete_records(airtable, base_uri, requests_mock, load):
    delete_responses = load("delete_responses")
    requests_mock.delete(base_uri, json=delete_responses)

    resp = airtable.delete_records(Table(delete_responses["records"]).cut("id"))

    assert len(resp) == len(delete_responses["records"])
    assert all(r["deleted"] for r in resp)
