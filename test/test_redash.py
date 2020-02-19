import unittest
import requests_mock
from test.utils import assert_matching_tables

from parsons.etl.table import Table
from parsons.redash.redash import Redash

BASE_URL = 'https://redash.example.com'
API_KEY = 'abc123'


class TestRedash(unittest.TestCase):

    def setUp(self):
        self.redash = Redash(BASE_URL, API_KEY)

    @requests_mock.Mocker()
    def test_cached_query(self, m):
        mock_data = 'foo,bar\n1,2\n3,4'
        m.get(f'{BASE_URL}/api/queries/5/results.csv', text=mock_data)
        self.assertEqual(self.redash.get_cached_query_results(5, API_KEY).text, mock_data)

    @requests_mock.Mocker()
    def test_refresh_query(self, m):
        mock_data = 'foo,bar\n1,2\n3,4'
        m.post(f'{BASE_URL}/api/queries/5/refresh', json={
            'job': {'status': 3, 'query_result_id': 21}})
        m.get(f'{BASE_URL}/api/queries/5/results/21.csv', text=mock_data)

        self.assertEqual(self.redash.get_fresh_query_results(5, {'yyy': 'xxx'}).text, mock_data)

    @requests_mock.Mocker()
    def test_refresh_query_poll(self, m):
        mock_data = 'foo,bar\n1,2\n3,4'
        m.post(f'{BASE_URL}/api/queries/5/refresh', json={
            'job': {'id': 66, 'status': 1}})
        m.get(f'{BASE_URL}/api/jobs/66', json={
            'job': {'id': 66, 'status': 3, 'query_result_id': 21}})
        m.get(f'{BASE_URL}/api/queries/5/results/21.csv', text=mock_data)

        self.redash.pause = 0.01  # shorten pause time
        self.assertEqual(self.redash.get_fresh_query_results(5, {'yyy': 'xxx'}).text, mock_data)

    @requests_mock.Mocker()
    def test_to_table(self, m):
        mock_data = 'foo,bar\n1,2\n3,4'
        m.post(f'{BASE_URL}/api/queries/5/refresh', json={
            'job': {'status': 3, 'query_result_id': 21}})
        m.get(f'{BASE_URL}/api/queries/5/results/21.csv', text=mock_data)

        self.redash.pause = 0.01  # shorten pause time
        table_data = Redash.load_to_table(
            base_url=BASE_URL,
            user_api_key=API_KEY,
            query_id=5,
            params={'x': 'y'},
            verify=False)

        assert_matching_tables(table_data, Table([('foo', 'bar'), ('1', '2'), ('3', '4')]))
