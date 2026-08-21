import pytest

from parsons import Quickbase

HOSTNAME = "test.example.com"
USER_TOKEN = "12345"


@pytest.fixture
def quickbase() -> Quickbase:
    """A Quickbase connector with a fake host/token (construction makes no request)."""
    return Quickbase(hostname=HOSTNAME, user_token=USER_TOKEN)
