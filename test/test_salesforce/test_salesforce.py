"""Tests for the Salesforce connector.

Reference example of the third-party SDK testing pattern (see
docs/write_tests.rst): pytest-native functions, a fixture that swaps the vendor
client for a mock, and per-test programming of the client methods under test.
"""

from parsons import Table


def test_describe_object(salesforce):
    salesforce._client.Contact.describe.return_value = {"name": "Contact", "fields": []}

    result = salesforce.describe_object("Contact")

    salesforce.client.Contact.describe.assert_called_once()
    assert result["name"] == "Contact"


def test_describe_fields(salesforce):
    salesforce._client.Contact.describe.return_value = {
        "fields": [{"name": "Id", "type": "id"}, {"name": "Email", "type": "email"}]
    }

    fields = salesforce.describe_fields("Contact")

    salesforce.client.Contact.describe.assert_called_once()
    assert fields == [{"name": "Id", "type": "id"}, {"name": "Email", "type": "email"}]


def test_query(salesforce):
    salesforce._client.query_all.return_value = {
        "totalSize": 1,
        "done": True,
        "records": [
            {
                "attributes": {
                    "type": "Contact",
                    "url": "/services/data/v38.0/sobjects/Contact/1234567890AaBbC",
                },
                "Id": "1234567890AaBbC",
            }
        ],
    }

    response = salesforce.query("FAKE SOQL")

    salesforce.client.query_all.assert_called_with("FAKE SOQL")
    assert response["records"][0]["Id"] == "1234567890AaBbC"


def test_insert(salesforce):
    salesforce._client.bulk.Contact.insert.return_value = [
        {"success": True, "created": True, "id": "1234567890AaBbC", "errors": []}
    ]
    data = Table([{"firstname": "Chrisjen", "lastname": "Avasarala"}])

    response = salesforce.insert_record("Contact", data)

    salesforce.client.bulk.Contact.insert.assert_called_with(data.to_dicts())
    assert response[0]["created"]


def test_update(salesforce):
    salesforce._client.bulk.Contact.update.return_value = [
        {"success": True, "created": False, "id": "1234567890AaBbC", "errors": []}
    ]
    data = Table([{"id": "1234567890AaBbC", "firstname": "Chrisjen", "lastname": "Avasarala"}])

    response = salesforce.update_record("Contact", data)

    salesforce.client.bulk.Contact.update.assert_called_with(data.to_dicts())
    assert not response[0]["created"]


def test_upsert(salesforce):
    salesforce._client.bulk.Contact.upsert.return_value = [
        {"success": True, "created": False, "id": "1234567890AaBbC", "errors": []},
        {"success": True, "created": True, "id": "1234567890AaBbc", "errors": []},
    ]
    data = Table(
        [
            {"id": "1234567890AaBbC", "firstname": "Chrisjen", "lastname": "Avasarala"},
            {"id": None, "firstname": "Roberta", "lastname": "Draper"},
        ]
    )

    response = salesforce.upsert_record("Contact", data, "id")

    salesforce.client.bulk.Contact.upsert.assert_called_with(data.to_dicts(), "id")
    assert not response[0]["created"]
    assert response[1]["created"]


def test_delete(salesforce):
    salesforce._client.bulk.Contact.delete.return_value = [
        {"success": True, "created": False, "id": "1234567890AaBbC", "errors": []}
    ]
    data = Table([{"id": "1234567890AaBbC"}])

    response = salesforce.delete_record("Contact", data)

    salesforce.client.bulk.Contact.delete.assert_called_with(data.to_dicts())
    assert not response[0]["created"]
