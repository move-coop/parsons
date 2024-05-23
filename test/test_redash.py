import os
import unittest
import requests_mock
from test.utils import assert_matching_tables
from parsons import Table, Redash
from parsons.redash.redash import RedashTimeout


BASE_URL = "https://redash.example.com"
API_KEY = "abc123"


class TestRedash(unittest.TestCase):

    mock_data = "foo,bar\n1,2\n3,4"
    mock_data_source = {
        "id": 1,
        "name": "Data Source 1",
        "type": "redshift",
        "options": {
            "dbname": "db_name",
            "host": "host.example.com",
            "password": "--------",
            "port": 5439,
            "user": "username",
        },
    }
    mock_result = Table([("foo", "bar"), ("1", "2"), ("3", "4")])

    def setUp(self):
        self.redash = Redash(BASE_URL, API_KEY)

    @requests_mock.Mocker()
    def test_get_data_source(self, m):
        m.get(f"{BASE_URL}/api/data_sources/1", json=self.mock_data_source)
        assert self.redash.get_data_source(1) == self.mock_data_source

    @requests_mock.Mocker()
    def test_update_data_source(self, m):
        m.post(f"{BASE_URL}/api/data_sources/1", json=self.mock_data_source)
        self.redash.update_data_source(
            1,
            "Data Source 1",
            "redshift",
            "db_name",
            "host.example.com",
            "password",
            5439,
            "username",
        )
        assert m.call_count == 1

    @requests_mock.Mocker()
    def test_cached_query(self, m):
        redash = Redash(BASE_URL)  # no user_api_key
        m.get(f"{BASE_URL}/api/queries/5/results.csv", text=self.mock_data)
        assert_matching_tables(redash.get_cached_query_results(5, API_KEY), self.mock_result)
        self.assertEqual(m._adapter.last_request.path, "/api/queries/5/results.csv")
        self.assertEqual(m._adapter.last_request.query, "api_key=abc123")

        assert_matching_tables(self.redash.get_cached_query_results(5), self.mock_result)
        self.assertEqual(m._adapter.last_request.query, "")

    @requests_mock.Mocker()
    def test_refresh_query(self, m):
        m.post(
            f"{BASE_URL}/api/queries/5/refresh",
            json={"job": {"status": 3, "query_result_id": 21}},
        )
        m.get(f"{BASE_URL}/api/queries/5/results/21.csv", text=self.mock_data)

        assert_matching_tables(
            self.redash.get_fresh_query_results(5, {"yyy": "xxx"}), self.mock_result
        )

    @requests_mock.Mocker()
    def test_refresh_query_poll(self, m):
        m.post(f"{BASE_URL}/api/queries/5/refresh", json={"job": {"id": 66, "status": 1}})
        m.get(
            f"{BASE_URL}/api/jobs/66",
            json={"job": {"id": 66, "status": 3, "query_result_id": 21}},
        )
        m.get(f"{BASE_URL}/api/queries/5/results/21.csv", text=self.mock_data)

        self.redash.pause = 0.01  # shorten pause time
        assert_matching_tables(
            self.redash.get_fresh_query_results(5, {"yyy": "xxx"}), self.mock_result
        )

    @requests_mock.Mocker()
    def test_refresh_query_poll_timeout(self, m):
        m.post(f"{BASE_URL}/api/queries/5/refresh", json={"job": {"id": 66, "status": 1}})
        m.get(f"{BASE_URL}/api/jobs/66", json={"job": {"id": 66, "status": 1}})
        m.get(f"{BASE_URL}/api/queries/5/results/21.csv", text=self.mock_data)

        self.redash.pause = 0.01  # shorten pause time
        self.redash.timeout = 0.01  # timeout
        raised = False
        try:
            self.redash.get_fresh_query_results(5, {"yyy": "xxx"})
        except RedashTimeout:
            raised = True
        self.assertTrue(raised)

    @requests_mock.Mocker()
    def test_to_table(self, m):
        m.post(
            f"{BASE_URL}/api/queries/5/refresh",
            json={"job": {"status": 3, "query_result_id": 21}},
        )
        m.get(f"{BASE_URL}/api/queries/5/results/21.csv", text=self.mock_data)

        self.redash.pause = 0.01  # shorten pause time
        table_data = Redash.load_to_table(
            base_url=BASE_URL,
            user_api_key=API_KEY,
            query_id=5,
            params={"x": "y"},
            verify=False,
        )

        assert_matching_tables(table_data, self.mock_result)

    @requests_mock.Mocker()
    def test_to_table_env_vars(self, m):
        try:
            _environ = dict(os.environ)
            os.environ.update(
                {
                    "REDASH_BASE_URL": BASE_URL,
                    "REDASH_USER_API_KEY": API_KEY,
                    "REDASH_QUERY_ID": "5",
                    "REDASH_QUERY_PARAMS": "p_x=y",
                }
            )
            m.post(
                f"{BASE_URL}/api/queries/5/refresh",
                json={"job": {"status": 3, "query_result_id": 21}},
            )
            m.get(f"{BASE_URL}/api/queries/5/results/21.csv", text=self.mock_data)

            self.redash.pause = 0.01  # shorten pause time

            assert_matching_tables(Redash.load_to_table(), self.mock_result)
        finally:
            os.environ.clear()
            os.environ.update(_environ)
