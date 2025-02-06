import os
import unittest
from unittest import mock
import requests_mock
from parsons import Sisense

from test.test_sisense.test_data import (
    ENV_PARAMETERS,
    TEST_PUBLISH_SHARED_DASHBOARD,
    TEST_LIST_SHARED_DASHBOARDS,
    TEST_DELETE_SHARED_DASHBOARD,
)


class TestSisense(unittest.TestCase):
    def setUp(self):
        self.sisense = Sisense(site_name="my_site_name", api_key="my_api_key")

    @mock.patch.dict(os.environ, ENV_PARAMETERS)
    def test_init(self):
        sisense = Sisense()
        self.assertEqual(sisense.site_name, "my_site_name")
        self.assertEqual(sisense.api_key, "my_api_key")
        self.assertEqual(sisense.api.uri, "https://app.periscopedata.com/api/v1/")
        self.assertEqual(sisense.api.headers["HTTP-X-PARTNER-AUTH"], "my_site_name:my_api_key")

    @requests_mock.Mocker()
    def test_publish_shared_dashboard(self, m):
        m.post(
            f"{self.sisense.uri}shared_dashboard/create",
            json=TEST_PUBLISH_SHARED_DASHBOARD,
        )
        self.assertEqual(
            self.sisense.publish_shared_dashboard(dashboard_id="1234"),
            TEST_PUBLISH_SHARED_DASHBOARD,
        )  # noqa

    @requests_mock.Mocker()
    def test_list_shared_dashboards(self, m):
        m.post(f"{self.sisense.uri}shared_dashboard/list", json=TEST_LIST_SHARED_DASHBOARDS)
        self.assertEqual(
            self.sisense.list_shared_dashboards(dashboard_id="1234"),
            TEST_LIST_SHARED_DASHBOARDS,
        )  # noqa

    @requests_mock.Mocker()
    def test_delete_shared_dashboard(self, m):
        m.post(
            f"{self.sisense.uri}shared_dashboard/delete",
            json=TEST_DELETE_SHARED_DASHBOARD,
        )
        self.assertEqual(
            self.sisense.delete_shared_dashboard(token="abc"),
            TEST_DELETE_SHARED_DASHBOARD,
        )  # noqa
