import unittest
import requests_mock
from parsons import Table, Community
from unittest.mock import MagicMock


TEST_CLIENT_ID = "someuuid"
TEST_CLIENT_TOKEN = "somesecret"

TEST_FILENAME = "campaigns"
TEST_URI = "https://faketestingurl.com"
TEST_FULL_URL = f"{TEST_URI}/{TEST_FILENAME}.csv.gz"

TEST_GET_RESPONSE = """\"LEADER_ID\",\"DATE_DAY\",\"OUTBOUND_MESSAGE_TYPE\",\"MESSAGE_COUNT\",\"SEGMENT_COUNT\"\n\"6e83b266-899f-4a01-b39c-e614a4929df7\",\"2022-10-03\",\"FAN_ONBOARDING\",1,3\n"""

TEST_EXPECTED_COLUMNS = [
    "LEADER_ID",
    "DATE_DAY",
    "OUTBOUND_MESSAGE_TYPE",
    "MESSAGE_COUNT",
    "SEGMENT_COUNT",
]


class TestCommunity(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.com = Community(TEST_CLIENT_ID, TEST_CLIENT_TOKEN, TEST_URI)
        self.from_csv = Table.from_csv
        test_csv_data = Table.from_csv_string(
            open("test/test_community/test_community_data.csv").read()
        )
        Table.from_csv = MagicMock(name="mocked from_csv", return_value=test_csv_data)

    def tearDown(self):
        Table.from_csv = self.from_csv

    @requests_mock.Mocker()
    def test_successful_get_request(self, m):
        print(f"Test: {TEST_FULL_URL}")
        m.get(TEST_FULL_URL, json=TEST_GET_RESPONSE)

        assert self.com.get_request(filename=TEST_FILENAME) == TEST_GET_RESPONSE

    # test get resource
    @requests_mock.Mocker()
    def test_successful_get_data_export(self, m):

        print(f"Test URL: {TEST_FULL_URL}")
        m.get(TEST_FULL_URL, json=TEST_GET_RESPONSE)

        table = self.com.get_data_export(
            TEST_FILENAME,
        )
        assert TEST_EXPECTED_COLUMNS == table.columns