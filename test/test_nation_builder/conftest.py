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
