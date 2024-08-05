import unittest
import requests_mock
from parsons import Table, Community
from unittest.mock import MagicMock


TEST_CLIENT_ID = "someuuid"
TEST_CLIENT_TOKEN = "somesecret"

TEST_ID = "12345"
TEST_URI = "https://faketestingurl.com/example"

TEST_CSV_TYPE = "campaigns"

TEST_GET_RESPONSE = {
    "body": '"LEADER_ID","DATE_DAY","OUTBOUND_MESSAGE_TYPE","MESSAGE_COUNT","SEGMENT_COUNT"\n"6e83b266-899f-4a01-b39c-e614a4929df7","2022-10-03","FAN_ONBOARDING",1,3',
}


class TestCommunity(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.com = Community(TEST_CLIENT_ID, TEST_CLIENT_TOKEN, TEST_URI)
        self.from_csv = Table.from_csv
        test_csv_data = Table.from_csv_string(open("test/test_actblue/test_csv_data.csv").read())
        Table.from_csv = MagicMock(name="mocked from_csv", return_value=test_csv_data)

    def tearDown(self):
        Table.from_csv = self.from_csv

    @requests_mock.Mocker()
    def test_successful_get_request(self, m):
        m.get(f"{TEST_URI}/{TEST_CLIENT_ID}/{TEST_CSV_TYPE}.csv.gz", json=TEST_GET_RESPONSE)

        assert self.com.get_resource(resource=TEST_CSV_TYPE) == TEST_GET_RESPONSE
