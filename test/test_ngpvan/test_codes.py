import pytest
from requests.exceptions import HTTPError

from parsons import VAN
from test.conftest import assert_matching_tables


def test_get_codes(van: VAN, requests_mock):
    json = {
        "items": [
            {
                "codeId": 1004916,
                "parentCodeId": None,
                "name": "Data Entry",
                "description": "for test.",
                "codePath": "Data Entry",
                "createdByName": "",
                "dateCreated": "2018-07-13T15:16:00Z",
                "supportedEntities": None,
                "codeType": "Tag",
                "campaign": None,
                "contactType": None,
            }
        ],
        "nextPageLink": None,
        "count": 8,
    }

    requests_mock.get(van.connection.uri + "codes", json=json)
    assert_matching_tables(json["items"], van.get_codes())


def test_get_code(van: VAN, requests_mock):
    json = {
        "codeId": 1004916,
        "parentCodeId": None,
        "name": "Data Entry",
        "description": "for test.",
        "codePath": "Data Entry",
        "createdByName": "",
        "dateCreated": "2018-07-13T15:16:00Z",
        "supportedEntities": None,
        "codeType": "Tag",
        "campaign": None,
        "contactType": None,
    }

    requests_mock.get(van.connection.uri + "codes/1004916", json=json)
    assert json == van.get_code(1004916)


def test_get_code_types(van: VAN, requests_mock):
    json = ["Tag", "SourceCode"]
    requests_mock.get(van.connection.uri + "codeTypes", json=json)
    assert json == van.get_code_types()


def test_create_code(van: VAN, requests_mock):
    requests_mock.post(van.connection.uri + "codes", json=1004960, status_code=201)

    # Test that it doesn't throw and error
    r = van.create_code(
        "Test Code",
        supported_entities=[{"name": "Events", "is_searchable": True, "is_applicable": True}],
    )

    assert r == 1004960


def test_update_code(van: VAN, requests_mock):
    # Test a good input
    requests_mock.put(van.connection.uri + "codes/1004960", status_code=204)
    van.update_code(1004960, name="Test")

    # Test a bad input
    requests_mock.put(van.connection.uri + "codes/100496Q", status_code=404)
    with pytest.raises(HTTPError):
        van.update_code("100496Q")


def test_delete_code(van: VAN, requests_mock):
    # Test a good input
    requests_mock.delete(van.connection.uri + "codes/1004960", status_code=204)
    van.delete_code(1004960)

    # Test a bad input
    requests_mock.delete(van.connection.uri + "codes/100496Q", status_code=404)
    with pytest.raises(HTTPError):
        van.delete_code("100496Q")


def test_get_code_supported_entities(van: VAN, requests_mock):
    json = ["Contacts", "Events", "Locations"]
    requests_mock.get(van.connection.uri + "codes/supportedEntities", json=json)
    assert json == van.get_code_supported_entities()
