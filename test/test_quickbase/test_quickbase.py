from parsons.quickbase.quickbase import Quickbase
from test.test_quickbase import test_data
import unittest
import requests_mock


class TestQuickbase(unittest.TestCase):

    @requests_mock.Mocker()
    def test_get_app_tables(self, m):

        qb = Quickbase(hostname='test.example.com', user_token='12345')
        m.get(qb.hostname + f'/v1/tables?appId={qb.user_token}',
              json=test_data.test_get_app_tables)
        tbl = qb.get_app_tables(app_id='test')

        self.assertEqual(tbl.num_rows, 2)
