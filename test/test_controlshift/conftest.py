import pytest

from parsons import Controlshift

HOSTNAME = "https://test.example.com"


@pytest.fixture
def hostname() -> str:
    return HOSTNAME


@pytest.fixture
def controlshift(requests_mock) -> Controlshift:
    """A Controlshift connector.

    Construction performs an OAuth token exchange, so the token endpoint is
    mocked here before the client is built.
    """
    requests_mock.post(f"{HOSTNAME}/oauth/token", json={"access_token": "123"})
    return Controlshift(hostname=HOSTNAME, client_id="1234", client_secret="1234")
