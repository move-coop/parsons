import unittest

import requests_mock

from parsons import Quickbase
from test.test_quickbase import test_data


class TestQuickbase(unittest.TestCase):
    @requests_mock.Mocker()
    def test_get_app_tables(self, m):
        qb = Quickbase(hostname="test.example.com", user_token="12345")
        m.get(f"{qb.api_hostname}/tables?appId=test", json=test_data.test_get_app_tables)
        tbl = qb.get_app_tables(app_id="test")

        self.assertEqual(tbl.num_rows, 2)

    @requests_mock.Mocker()
    def test_query_records(self, m):
        qb = Quickbase(hostname="test.example.com", user_token="12345")
        m.post(f"{qb.api_hostname}/records/query", json=test_data.test_query_records)
        tbl = qb.query_records(table_from="test_table")

        self.assertEqual(tbl.num_rows, 1)
