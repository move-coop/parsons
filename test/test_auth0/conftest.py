import pytest

from parsons import Auth0

CLIENT_ID = "abc"
CLIENT_SECRET = "def"
DOMAIN = "fakedomain.auth0.com"
BASE_URL = f"https://{DOMAIN}"


@pytest.fixture
def auth0(requests_mock) -> Auth0:
    """
    An Auth0 connector with its OAuth token handshake mocked.

    The connector calls ``requests`` directly, so tests mock the HTTP boundary
    with the ``requests_mock`` fixture. The constructor POSTs for an access
    token, which is registered here.
    """
    requests_mock.post(f"{BASE_URL}/oauth/token", json={"access_token": "fake_token"})
    return Auth0(CLIENT_ID, CLIENT_SECRET, DOMAIN)
