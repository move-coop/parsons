import json

import pytest

from parsons import Hustle
from parsons.hustle.hustle import HUSTLE_URI

CLIENT_ID = "FAKE_ID"
CLIENT_SECRET = "FAKE_SECRET"


@pytest.fixture
def load(shared_datadir):
    """Load a canned Hustle response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load


@pytest.fixture
def hustle(requests_mock, load) -> Hustle:
    """A Hustle connector.

    The constructor performs an OAuth token exchange, so the token endpoint is
    mocked here before the client is built.
    """
    requests_mock.post(HUSTLE_URI + "oauth/token", json=load("auth_token"))
    return Hustle(CLIENT_ID, CLIENT_SECRET)
