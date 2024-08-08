import unittest
import requests_mock
from parsons import Table, Community
from unittest.mock import MagicMock


TEST_CLIENT_ID = "someuuid"
TEST_CLIENT_TOKEN = "somesecret"

TEST_ID = "12345"

TEST_CSV_TYPE = "campaigns"
TEST_URI = f"https://faketestingurl.com/"

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
        m.get(f"{TEST_URI}/{TEST_CLIENT_ID}/{TEST_CSV_TYPE}.csv.gz", json=TEST_GET_RESPONSE)

        assert self.com.get_request(filename=TEST_CSV_TYPE) == TEST_GET_RESPONSE

    # test get resource
    @requests_mock.Mocker()
    def test_successful_get_data_export(self, m):
        m.get(f"{TEST_URI}/{TEST_CLIENT_ID}/{TEST_CSV_TYPE}.csv.gz", json=TEST_GET_RESPONSE)

        table = self.com.get_data_export(
            TEST_CSV_TYPE,
        )
        assert TEST_EXPECTED_COLUMNS == table.columns
