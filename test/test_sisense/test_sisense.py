import os
import unittest
from unittest import mock
import requests_mock
from parsons.sisense.sisense import Sisense
from parsons.etl import Table

from test.utils import assert_matching_tables
from test.test_sisense.test_data import ENV_PARAMETERS, \
    TEST_GET_DASHBOARDS, TEST_GET_DASHBOARD_SHARES, \
    TEST_PUBLISH_DASHBOARD_BLOB, TEST_PUBLISH_DASHBOARD_URL


class TestSisense(unittest.TestCase):

    def setUp(self):
        self.sisense = Sisense(site_name='my_site_name', api_key='my_api_key')

    @mock.patch.dict(os.environ, ENV_PARAMETERS)
    def test_init(self):
        sisense = Sisense()
        self.assertEqual(sisense.site_name, 'my_site_name')
        self.assertEqual(sisense.api_key, 'my_api_key')
        self.assertEqual(sisense.api.uri, 'https://app.periscopedata.com/api/v1/')
        self.assertEqual(sisense.api.headers['HTTP-X-PARTNER-AUTH'], 'my_site_name:my_api_key')

    @requests_mock.Mocker()
    def test_get_dashboards(self, m):
        m.get(f'{self.sisense.uri}dashboards', json=TEST_GET_DASHBOARDS)
        assert_matching_tables(self.sisense.get_dashboards(), Table(TEST_GET_DASHBOARDS))

        m.get(f'{self.sisense.uri}dashboards/123', json=TEST_GET_DASHBOARDS)
        assert_matching_tables(self.sisense.get_dashboards(123), Table(TEST_GET_DASHBOARDS))

        m.get(f'{self.sisense.uri}dashboards/123', json=TEST_GET_DASHBOARDS)
        assert_matching_tables(self.sisense.get_dashboards('123'), Table(TEST_GET_DASHBOARDS))

    @requests_mock.Mocker()
    def test_get_dashboard_shares(self, m):
        m.get(f'{self.sisense.uri}dashboards/123/shares', json=TEST_GET_DASHBOARD_SHARES)
        assert_matching_tables(self.sisense.get_dashboard_shares(dashboard_id=123), Table(TEST_GET_DASHBOARD_SHARES))  # noqa

        m.get(f'{self.sisense.uri}dashboards/123/shares/456', json=TEST_GET_DASHBOARD_SHARES)
        assert_matching_tables(self.sisense.get_dashboard_shares(dashboard_id=123, share_id=456), Table(TEST_GET_DASHBOARD_SHARES)) # noqa

        m.get(f'{self.sisense.uri}dashboards/123/shares/456', json=TEST_GET_DASHBOARD_SHARES)
        assert_matching_tables(self.sisense.get_dashboard_shares(dashboard_id='123', share_id='456'), Table(TEST_GET_DASHBOARD_SHARES))  # noqa

    @requests_mock.Mocker()
    def test_publish_dashboard(self, m):
        m.post(f'{self.sisense.uri}shared_dashboard/create', json=TEST_PUBLISH_DASHBOARD_URL)
        self.assertEqual(self.sisense.publish_dashboard(TEST_PUBLISH_DASHBOARD_BLOB), TEST_PUBLISH_DASHBOARD_URL['url']) # noqa
