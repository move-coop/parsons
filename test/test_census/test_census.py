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

    @mark_live_test
    @patch.dict(os.environ, {"CENSUS_API_KEY": "mock_api_key"})
    def test_get_census_live_test(self):
        year = "2019"
        dataset_acronym = "/acs/acs1"
        variables = "NAME,B01001_001E"
        location = "for=state:*"
        table = self.census.get_census(year, dataset_acronym, variables, location)
        self.assertEqual(len(table), 52)
        self.assertEqual(table[0]["NAME"], "Illinois")
        self.assertIsInstance(table, Table)

    @patch.dict(os.environ, {"CENSUS_API_KEY": "mock_api_key"})
    @requests_mock.Mocker()
    def test_get_census_mock_test(self, m):
        census = Census()
        year = "2019"
        dataset_acronym = "/acs/acs1"
        variables = "NAME,B01001_001E"
        location = "for=us:1"
        test_json = {"NAME": "United States", "B01001_001E": "328239523", "us": "1"}
        table = m.census.get_census(year, dataset_acronym, variables, location, json=test_json)
        self.assertEqual(table[0]["B01001_001E"], "328239523")
        self.assertEqual(table[0]["NAME"], "United States")
