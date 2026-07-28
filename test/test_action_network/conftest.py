import json

import pytest

from parsons.action_network import ActionNetwork


@pytest.fixture
def an() -> ActionNetwork:
    """An ActionNetwork connector with a fake token (construction makes no request)."""
    return ActionNetwork("fake_key")


@pytest.fixture
def load(shared_datadir):
    """Load a canned Action Network response payload from the ``data/`` directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
