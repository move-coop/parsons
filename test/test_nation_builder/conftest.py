import json

import pytest

from parsons import NationBuilder

SLUG = "test-slug"
TOKEN = "test-token"
BASE_URL = f"https://{SLUG}.nationbuilder.com/api/v1"


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def nb() -> NationBuilder:
    """A NationBuilder connector with fake credentials (construction makes no request)."""
    return NationBuilder(SLUG, TOKEN)


@pytest.fixture
def load(shared_datadir):
    """Load a canned NationBuilder response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
