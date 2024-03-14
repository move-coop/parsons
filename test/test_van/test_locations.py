import unittest
import os
import requests_mock
from parsons import VAN
from test.utils import validate_list
from requests.exceptions import HTTPError


os.environ["VAN_API_KEY"] = "SOME_KEY"


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


class TestLocations(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="EveryAction", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_locations(self, m):

        json = {"items": [location_json], "nextPageLink": None, "count": 1}
        m.get(self.van.connection.uri + "locations", json=json)

        self.assertTrue(validate_list(expected_loc, self.van.get_locations()))

    @requests_mock.Mocker()
    def test_get_location(self, m):

        # Valid location id
        m.get(self.van.connection.uri + "locations/34", json=location_json)
        self.assertEqual(location_json, self.van.get_location(34))

    @requests_mock.Mocker()
    def test_delete_location(self, m):

        # Test good location delete
        m.delete(self.van.connection.uri + "locations/1", status_code=200)
        self.van.delete_location(1)

        # Test invalid location delete
        m.delete(self.van.connection.uri + "locations/2", status_code=404)
        self.assertRaises(HTTPError, self.van.delete_location, 2)

    @requests_mock.Mocker()
    def test_create_location(self, m):

        loc_id = 32

        m.post(
            self.van.connection.uri + "locations/findOrCreate",
            json=loc_id,
            status_code=204,
        )

        self.assertEqual(
            self.van.create_location(name="Chicagowide", city="Chicago", state="IL"),
            loc_id,
        )
