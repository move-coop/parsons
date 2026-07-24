import json

import pytest

from parsons import Formstack


@pytest.fixture
def formstack() -> Formstack:
    """A Formstack connector with a fake token (construction makes no request)."""
    return Formstack(api_token="token")


@pytest.fixture
def load(shared_datadir):
    """Load a canned Formstack response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
