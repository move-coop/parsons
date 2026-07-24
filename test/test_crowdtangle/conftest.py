import json

import pytest

from parsons import CrowdTangle


@pytest.fixture
def crowdtangle() -> CrowdTangle:
    """A CrowdTangle connector with a fake key (construction makes no request)."""
    return CrowdTangle("FAKE_KEY")


@pytest.fixture
def load(shared_datadir):
    """Load a canned CrowdTangle response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
