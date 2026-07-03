import pytest

from parsons import Airmeet

# The connector wraps APIConnector, which issues its requests through
# `requests` — so tests mock at the HTTP layer with the `requests_mock` fixture.
BASE_URI = "https://api-gateway.airmeet.com/prod/"


@pytest.fixture
def airmeet(requests_mock) -> Airmeet:
    """
    An Airmeet connector with its auth handshake mocked.

    The constructor POSTs to the ``auth`` endpoint and stores the returned token,
    so that request is registered here. Tests register the data endpoints they
    exercise on the same ``requests_mock`` fixture.
    """
    requests_mock.post(f"{BASE_URI}auth", json={"token": "test_token"})
    return Airmeet(airmeet_access_key="fake_key", airmeet_secret_key="fake_secret")
