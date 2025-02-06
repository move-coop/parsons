import unittest

import requests_mock

from parsons import Community

TEST_CLIENT_ID = "someuuid"
TEST_CLIENT_TOKEN = "somesecret"

TEST_FILENAME = "campaigns"
TEST_URI = f"https://faketestingurl.com/{TEST_CLIENT_ID}"
TEST_FULL_URL = f"{TEST_URI}/{TEST_FILENAME}.csv.gz"

TEST_GET_RESPONSE_CSV_STRING = b'"CAMPAIGN_ID","LEADER_ID"\n"0288","6e83b"\n'

TEST_EXPECTED_COLUMNS = [
    "CAMPAIGN_ID",
    "LEADER_ID",
]


class TestCommunity(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.com = Community(TEST_CLIENT_ID, TEST_CLIENT_TOKEN, TEST_URI)

    @requests_mock.Mocker()
    def test_successful_get_request(self, m):
        m.get(TEST_FULL_URL, content=TEST_GET_RESPONSE_CSV_STRING)

        assert self.com.get_request(filename=TEST_FILENAME) == TEST_GET_RESPONSE_CSV_STRING

    # test get resource
    @requests_mock.Mocker()
    def test_successful_get_data_export(self, m):
        m.get(TEST_FULL_URL, content=TEST_GET_RESPONSE_CSV_STRING)

        table = self.com.get_data_export(
            TEST_FILENAME,
        )
        assert TEST_EXPECTED_COLUMNS == table.columns
