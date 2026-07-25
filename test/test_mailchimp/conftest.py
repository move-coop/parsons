import json

import pytest

from parsons import Mailchimp

API_KEY = "mykey-us00"


@pytest.fixture
def mailchimp() -> Mailchimp:
    """A Mailchimp connector with a fake key (construction makes no request)."""
    return Mailchimp(API_KEY)


@pytest.fixture
def load(shared_datadir):
    """Load a canned Mailchimp response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
