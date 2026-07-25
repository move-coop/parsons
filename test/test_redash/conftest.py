import pytest

from parsons import Redash

BASE_URL = "https://redash.example.com"
API_KEY = "abc123"


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def redash() -> Redash:
    """A Redash connector with fake credentials (construction makes no request)."""
    return Redash(BASE_URL, API_KEY)
