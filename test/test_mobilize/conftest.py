import json

import pytest

from parsons import MobilizeAmerica


@pytest.fixture
def mobilize() -> MobilizeAmerica:
    """A MobilizeAmerica connector (construction makes no request)."""
    return MobilizeAmerica(api_key="test_password")


@pytest.fixture
def load(shared_datadir):
    """Load a canned Mobilize America response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
