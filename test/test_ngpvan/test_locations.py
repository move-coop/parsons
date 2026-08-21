import pytest
from requests.exceptions import HTTPError

from parsons import VAN
from test.conftest import validate_list

location_json = {
    "locationId": 34,
    "name": "Chicagowide",
    "displayName": "Chicagowide, Chicago, IL ",
    "address": {
        "addressId": None,
        "addressLine1": None,
        "addressLine2": None,
        "addressLine3": None,
        "city": "Chicago",
        "stateOrProvince": "IL",
        "zipOrPostalCode": None,
        "geoLocation": None,
        "countryCode": "US",
        "preview": "Chicago, IL ",
        "type": None,
        "isPreferred": None,
        "streetAddress": None,
        "displayMode": "Standardized",
    },
    "id": 34,
    "notes": None,
    "codes": None,
}

expected_loc = [
    "locationId",
    "name",
    "displayName",
    "id",
    "notes",
    "codes",
    "addressId",
    "addressLine1",
    "addressLine2",
    "addressLine3",
    "city",
    "countryCode",
    "displayMode",
    "isPreferred",
    "preview",
    "stateOrProvince",
    "streetAddress",
    "type",
    "zipOrPostalCode",
]


def test_get_locations(van_everyaction: VAN, requests_mock):
    van = van_everyaction
    json = {"items": [location_json], "nextPageLink": None, "count": 1}
    requests_mock.get(van.connection.uri + "locations", json=json)

    assert validate_list(expected_loc, van.get_locations())


def test_get_location(van_everyaction: VAN, requests_mock):
    van = van_everyaction
    # Valid location id
    requests_mock.get(van.connection.uri + "locations/34", json=location_json)
    assert location_json == van.get_location(34)


def test_delete_location(van_everyaction: VAN, requests_mock):
    van = van_everyaction
    # Test good location delete
    requests_mock.delete(van.connection.uri + "locations/1", status_code=200)
    van.delete_location(1)

    # Test invalid location delete
    requests_mock.delete(van.connection.uri + "locations/2", status_code=404)
    with pytest.raises(HTTPError):
        van.delete_location(2)


def test_create_location(van_everyaction: VAN, requests_mock):
    van = van_everyaction
    loc_id = 32

    requests_mock.post(
        van.connection.uri + "locations/findOrCreate",
        json=loc_id,
        status_code=204,
    )

    assert van.create_location(name="Chicagowide", city="Chicago", state="IL") == loc_id
