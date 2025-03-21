import unittest

import pytest
import requests_mock
from googlecivic_responses import (
    elections_resp,
    polling_data,
    representatives_resp,
    voterinfo_resp,
)

from parsons import GoogleCivic, Table
from test.utils import assert_matching_tables


class TestGoogleCivic(unittest.TestCase):
    def setUp(self):
        self.gc = GoogleCivic(api_key="FAKEKEY")

    @requests_mock.Mocker()
    def test_get_elections(self, m):
        m.get(self.gc.uri + "elections", json=elections_resp)

        expected_tbl = Table(elections_resp["elections"])

        assert_matching_tables(self.gc.get_elections(), expected_tbl)

    @requests_mock.Mocker()
    def test_get_poll_location(self, m):
        m.get(self.gc.uri + "voterinfo", json=voterinfo_resp)

        expected_tbl = Table(voterinfo_resp["pollingLocations"])

        tbl = self.gc.get_polling_location(2000, "900 N Washtenaw, Chicago, IL 60622")

        assert_matching_tables(tbl, expected_tbl)

    @requests_mock.Mocker()
    def test_get_poll_locations(self, m):
        m.get(self.gc.uri + "voterinfo", json=voterinfo_resp)

        expected_tbl = Table(polling_data)

        address_tbl = Table(
            [
                ["address"],
                ["900 N Washtenaw, Chicago, IL 60622"],
                ["900 N Washtenaw, Chicago, IL 60622"],
            ]
        )

        tbl = self.gc.get_polling_locations(2000, address_tbl)

        assert_matching_tables(tbl, expected_tbl)

    @requests_mock.Mocker()
    def test_get_representative_info_by_address(self, m):
        m.get(self.gc.uri + "representatives", json=representatives_resp)

        address = "1600 Amphitheatre Parkway, Mountain View, CA"  # replace with a valid address
        response = self.gc.get_representative_info_by_address(address)

        assert isinstance(response, dict)
        assert "offices" in response
        assert "officials" in response
        assert "divisions" in response

    @requests_mock.Mocker()
    def test_get_representative_info_by_address_invalid_input(self, m):
        m.get(self.gc.uri + "representatives", json=representatives_resp)

        with pytest.raises(ValueError):
            self.gc.get_representative_info_by_address(123)  # Invalid address

        with pytest.raises(ValueError):
            self.gc.get_representative_info_by_address(
                "1600 Amphitheatre Parkway, Mountain View, CA", levels="country"
            )  # levels should be a list

        with pytest.raises(ValueError):
            self.gc.get_representative_info_by_address(
                "1600 Amphitheatre Parkway, Mountain View, CA", roles="headOfGovernment"
            )  # roles should be a list

    @requests_mock.Mocker()
    def test_get_representative_info_by_address_different_params(self, m):
        m.get(self.gc.uri + "representatives", json=representatives_resp)

        address = "1600 Amphitheatre Parkway, Mountain View, CA"
        response = self.gc.get_representative_info_by_address(
            address,
            include_offices=False,
            levels=["country"],
            roles=["headOfGovernment"],
        )

        assert isinstance(response, dict)
        assert "offices" in response
        assert "officials" in response
        assert "divisions" in response
