import pytest

from parsons import Freshdesk

DOMAIN = "myorg"
API_KEY = "mykey"


@pytest.fixture
def freshdesk() -> Freshdesk:
    """A Freshdesk connector with fake credentials (construction makes no request)."""
    return Freshdesk(DOMAIN, API_KEY)
