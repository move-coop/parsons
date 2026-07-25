import json

import pytest

from parsons import CapitolCanary


@pytest.fixture
def cc() -> CapitolCanary:
    """A CapitolCanary connector with fake credentials (construction makes no request)."""
    return CapitolCanary(app_id="an_id", app_key="app_key")


@pytest.fixture
def load(shared_datadir):
    """Load a canned CapitolCanary response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
