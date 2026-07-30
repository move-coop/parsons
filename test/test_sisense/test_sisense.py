"""Tests for the Sisense connector.

Sisense is built on APIConnector, so tests mock the HTTP boundary with the
``requests_mock`` fixture (see docs/contrib_docs/write_tests.rst).
"""

from parsons import Sisense
from test.test_sisense.test_data import (
    ENV_PARAMETERS,
    TEST_DELETE_SHARED_DASHBOARD,
    TEST_LIST_SHARED_DASHBOARDS,
    TEST_PUBLISH_SHARED_DASHBOARD,
)


def test_init(monkeypatch):
    for key, value in ENV_PARAMETERS.items():
        monkeypatch.setenv(key, value)

    sisense = Sisense()

    assert sisense.site_name == "my_site_name"
    assert sisense.api_key == "my_api_key"
    assert sisense.api.uri == "https://app.periscopedata.com/api/v1/"
    assert sisense.api.headers["HTTP-X-PARTNER-AUTH"] == "my_site_name:my_api_key"


def test_publish_shared_dashboard(sisense, requests_mock):
    requests_mock.post(f"{sisense.uri}shared_dashboard/create", json=TEST_PUBLISH_SHARED_DASHBOARD)

    assert sisense.publish_shared_dashboard(dashboard_id="1234") == TEST_PUBLISH_SHARED_DASHBOARD


def test_list_shared_dashboards(sisense, requests_mock):
    requests_mock.post(f"{sisense.uri}shared_dashboard/list", json=TEST_LIST_SHARED_DASHBOARDS)

    assert sisense.list_shared_dashboards(dashboard_id="1234") == TEST_LIST_SHARED_DASHBOARDS


def test_delete_shared_dashboard(sisense, requests_mock):
    requests_mock.post(f"{sisense.uri}shared_dashboard/delete", json=TEST_DELETE_SHARED_DASHBOARD)

    assert sisense.delete_shared_dashboard(token="abc") == TEST_DELETE_SHARED_DASHBOARD
