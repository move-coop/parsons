import unittest
import requests_mock
import json
from parsons import Table, ActBlue
from test.utils import validate_list
from test.test_actblue import test_columns_data
from unittest.mock import MagicMock


TEST_CLIENT_UUID='someuuid'
TEST_CLIENT_SECRET='somesecret'

TEST_ID = '12345'
TEST_URI = 'https://faketestingurl.com/example'

TEST_CSV_TYPE = 'refunded_contributions'
TEST_DATE_RANGE_START = '2017-07-07'
TEST_DATE_RANGE_END = '2017-08-07'

TEST_POST_RESPONSE = {
    "id": TEST_ID
}

TEST_GET_RESPONSE = {
    "id": TEST_ID,
    "download_url": "https://www.example.com/example.csv",
    "status": "complete"
}

class TestActBlue(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):
        self.ab = ActBlue(TEST_CLIENT_UUID, TEST_CLIENT_SECRET, TEST_URI)


    @requests_mock.Mocker()
    def test_successful_post_request(self, m):
        m.post(f'{TEST_URI}/csvs', json=TEST_POST_RESPONSE)

        response = self.ab.post_request(TEST_CSV_TYPE, TEST_DATE_RANGE_START, TEST_DATE_RANGE_END)
        assert response['id'] == TEST_POST_RESPONSE['id']

    
    @requests_mock.Mocker()
    def test_successful_get_download_url(self, m):
        m.get(f'{TEST_URI}/csvs/{TEST_ID}', json=TEST_GET_RESPONSE)

        assert self.ab.get_download_url(csv_id=TEST_ID) == "https://www.example.com/example.csv"


    @requests_mock.Mocker()
    def test_successful_poll_for_download_url(self, m):
        mocked_get_response_no_download_url =   {
            "id": TEST_ID,
            "download_url": None,
            "status": "in_progress"
        }

        m.get(f'{TEST_URI}/csvs/{TEST_ID}', [{ 'json': mocked_get_response_no_download_url },
                                             { 'json': TEST_GET_RESPONSE }])

        assert self.ab.poll_for_download_url(csv_id=TEST_ID) == "https://www.example.com/example.csv"

        
    @requests_mock.Mocker()
    def test_successful_get_contributions(self, m):
        # setting up all necessary mock responses 
        m.post(f'{TEST_URI}/csvs', json=TEST_POST_RESPONSE)

        m.get(f'{TEST_URI}/csvs/{TEST_ID}', json=TEST_GET_RESPONSE)

        tbl = Table.from_csv_string(open('test/test_actblue/test_csv_data.csv').read())
        Table.from_csv = MagicMock()
        Table.from_csv.return_value = tbl

        # running actual test
        table = self.ab.get_contributions(TEST_CSV_TYPE, TEST_DATE_RANGE_START, TEST_DATE_RANGE_END)
        assert test_columns_data.expected_table_columns == table.columns
