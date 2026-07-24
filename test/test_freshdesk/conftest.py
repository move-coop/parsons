import json

import pytest

from parsons import Freshdesk

DOMAIN = "myorg"
API_KEY = "mykey"


@pytest.fixture
def freshdesk() -> Freshdesk:
    """A Freshdesk connector with fake credentials (construction makes no request)."""
    return Freshdesk(DOMAIN, API_KEY)


@pytest.fixture
def load(shared_datadir):
    """Load a canned Freshdesk response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
