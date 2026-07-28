import json

import pytest

from parsons import BillCom

API_URL = "http://FAKEURL.com/"


@pytest.fixture
def api_url() -> str:
    return API_URL


@pytest.fixture
def bc(requests_mock) -> BillCom:
    """A BillCom connector.

    Construction posts to Login.json to obtain a session id, so that endpoint is
    mocked here before the client is built.
    """
    requests_mock.post(API_URL + "Login.json", json={"response_data": {"sessionId": "FAKE"}})
    return BillCom("FAKE", "FAKE", "FAKE", "FAKE", API_URL)


@pytest.fixture
def load(shared_datadir):
    """Load a canned Bill.com response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
