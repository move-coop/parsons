import json

import pytest

from parsons import Phone2Action


@pytest.fixture
def p2a() -> Phone2Action:
    """A Phone2Action connector with fake credentials (construction makes no request)."""
    return Phone2Action(app_id="an_id", app_key="app_key")


@pytest.fixture
def load(shared_datadir):
    """Load a canned Phone2Action response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
