import unittest
import requests_mock
from parsons import Table, Community
from unittest.mock import MagicMock


TEST_CLIENT_ID = "someuuid"
TEST_CLIENT_TOKEN = "somesecret"

TEST_FILENAME = "campaigns"
TEST_URI = f"https://faketestingurl.com/{TEST_CLIENT_ID}"
TEST_FULL_URL = f"{TEST_URI}/{TEST_FILENAME}.csv.gz"

TEST_GET_RESPONSE = b'"CAMPAIGN_ID","LEADER_ID"\n"0288eb25-d795-4ca1-b90f-379ecccb42ad","6e83b266-899f-4a01-b39c-e614a4929df7"\n'

TEST_EXPECTED_COLUMNS = [
    "CAMPAIGN_ID",
    "LEADER_ID",
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
        m.get(TEST_FULL_URL, content=TEST_GET_RESPONSE)

        assert self.com.get_request(filename=TEST_FILENAME) == TEST_GET_RESPONSE

    # test get resource
    @requests_mock.Mocker()
    def test_successful_get_data_export(self, m):

        print(f"Test URL: {TEST_FULL_URL}")
        m.get(TEST_FULL_URL, content=TEST_GET_RESPONSE)

        table = self.com.get_data_export(
            TEST_FILENAME,
        )
        assert TEST_EXPECTED_COLUMNS == table.columns
