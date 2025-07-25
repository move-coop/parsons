import os
import unittest
from unittest import mock

import petl
from test_responses import batch_resp, coord_resp, geographies_resp, locations_resp

from parsons import CensusGeocoder, Table
from test.utils import assert_matching_tables


@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestCensusGeocoder(unittest.TestCase):
    def setUp(self):
        self.cg = CensusGeocoder()

    def test_geocode_onelineaddress(self):
        self.cg.cg = mock.MagicMock()
        address = "1600 Pennsylvania Avenue, Washington, DC"

        # Assert one line with geographies parameter returns expected
        self.cg.cg.onelineaddress = mock.MagicMock(return_value=geographies_resp)
        geo = self.cg.geocode_onelineaddress(address, return_type="geographies")
        self.cg.cg.onelineaddress.assert_called_with(address, returntype="geographies")
        assert geo == geographies_resp

        # Assert one line with locations parameter returns expected
        self.cg.cg.onelineaddress = mock.MagicMock(return_value=locations_resp)
        geo = self.cg.geocode_onelineaddress(address, return_type="locations")
        self.cg.cg.onelineaddress.assert_called_with(address, returntype="locations")
        assert geo == locations_resp

    def test_geocode_address(self):
        self.cg.cg = mock.MagicMock()
        passed_address = {
            "address_line": "1600 Pennsylvania Avenue",
            "city": "Washington",
            "state": "DC",
        }

        # Assert one line with geographies parameter returns expected
        self.cg.cg.address = mock.MagicMock(return_value=geographies_resp)
        geo = self.cg.geocode_address(**passed_address, return_type="geographies")
        assert geo == geographies_resp

        # Assert one line with locations parameter returns expected
        self.cg.cg.address = mock.MagicMock(return_value=locations_resp)
        geo = self.cg.geocode_address(**passed_address, return_type="locations")
        assert geo == locations_resp

    def test_geocode_address_batch(self):
        batch = [
            ["id", "street", "city", "state", "zip"],
            ["1", "908 N Washtenaw", "Chicago", "IL", "60622"],
            ["2", "1405 Wilshire Blvd", "Austin", "TX", "78722"],
            ["3", "908 N Washtenaw", "Chicago", "IL", "60622"],
            ["4", "1405 Wilshire Blvd", "Austin", "TX", "78722"],
            ["5", "908 N Washtenaw", "Chicago", "IL", "60622"],
        ]

        tbl = Table(batch)

        self.cg.cg.addressbatch = mock.MagicMock(return_value=batch_resp)
        geo = self.cg.geocode_address_batch(tbl)
        assert_matching_tables(geo, Table(petl.fromdicts(batch_resp)))

    def test_coordinates(self):
        # Assert coordinates data returns expected response.
        self.cg.cg.address = mock.MagicMock(return_value=coord_resp)
        geo = self.cg.get_coordinates_data("38.8884212", "-77.0441907")
        assert geo == coord_resp
