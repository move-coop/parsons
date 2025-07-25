import os
import unittest
from unittest.mock import patch

import requests_mock

from parsons import Census, Table
from test.utils import mark_live_test


class TestCensus(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch.dict(os.environ, {"CENSUS_API_KEY": "mock_api_key"})
    @mark_live_test
    def test_get_census_live_test(self):
        self.census = Census()
        year = "2019"
        dataset_acronym = "/acs/acs1"
        variables = "NAME,B01001_001E"
        location = "for=state:*"
        table = self.census.get_census(year, dataset_acronym, variables, location)
        assert len(table) == 52
        assert table[0]["NAME"] == "Illinois"
        assert isinstance(table, Table)

    @patch.dict(os.environ, {"CENSUS_API_KEY": "mock_api_key"})
    @requests_mock.Mocker()
    def test_get_census_mock_test(self, m):
        census = Census()
        year = "2019"
        dataset_acronym = "/acs/acs1"
        variables = "NAME,B01001_001E"
        location = "us:1"

        # This must match what get_census() will call under the hood
        expected_url = (
            "https://api.census.gov/data/2019/acs/acs1"
            "?get=NAME,B01001_001E&for=us:1&key=mock_api_key"
        )

        # Mock the actual HTTP response
        m.get(
            expected_url, json=[["NAME", "B01001_001E", "us"], ["United States", "328239523", "1"]]
        )

        table = census.get_census(year, dataset_acronym, variables, location)

        assert table[0]["B01001_001E"] == "328239523"
        assert table[0]["NAME"] == "United States"
