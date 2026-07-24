import json

import pytest

from parsons import Empower

API_KEY = "MYKEY"
API_ENDPOINT = "https://api.getempower.com/v1/export"


@pytest.fixture
def export_data(shared_datadir) -> dict:
    """The canned Empower export payload."""
    return json.loads((shared_datadir / "export.json").read_text())


@pytest.fixture
def empower(requests_mock, export_data) -> Empower:
    """An Empower connector.

    Empower fetches the whole export once at construction and caches it, so the
    endpoint is mocked here rather than in each test.
    """
    requests_mock.get(API_ENDPOINT, json=export_data)
    return Empower(api_key=API_KEY)
