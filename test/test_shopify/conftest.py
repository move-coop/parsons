import pytest

from parsons import Shopify

SUBDOMAIN = "myorg"
PASSWORD = "abc123"
API_KEY = "abc123"
API_VERSION = "2020-10"


@pytest.fixture
def subdomain() -> str:
    return SUBDOMAIN


@pytest.fixture
def api_version() -> str:
    return API_VERSION


@pytest.fixture
def shopify() -> Shopify:
    """A Shopify connector with fake credentials (construction makes no request)."""
    return Shopify(SUBDOMAIN, PASSWORD, API_KEY, API_VERSION)
