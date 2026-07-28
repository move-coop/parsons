import json

import pytest

from parsons import Copper


@pytest.fixture
def copper() -> Copper:
    """A Copper connector with fake credentials (construction makes no request)."""
    return Copper("usr@losr.fake", "key")


@pytest.fixture
def load(shared_datadir):
    """Load a canned Copper response payload from the ``data/`` directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load


@pytest.fixture(autouse=True)
def _no_sleep(mocker):
    """``paginate_request`` sleeps 1s per page to respect rate limits; skip it in tests."""
    mocker.patch("parsons.copper.copper.time.sleep")
