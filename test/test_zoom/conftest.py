import pytest

from parsons import Zoom

# Zoom is built on OAuth2APIConnector, which issues its requests through
# `requests` — so tests mock at the HTTP layer with the `requests_mock` fixture.
ACCOUNT_ID = "fakeAccountID"
CLIENT_ID = "fakeClientID"
CLIENT_SECRET = "fakeClientSecret"

ZOOM_URI = "https://api.zoom.us/v2/"
ZOOM_AUTH_CALLBACK = "https://zoom.us/oauth/token"


@pytest.fixture
def zoom(requests_mock):
    """
    A Zoom (v1) connector with its OAuth handshake mocked.

    The constructor POSTs to the OAuth token endpoint to obtain an access token,
    so that request is registered here. Tests register the data endpoints they
    exercise on the same ``requests_mock`` fixture.
    """
    requests_mock.post(ZOOM_AUTH_CALLBACK, json={"access_token": "fakeAccessToken"})
    return Zoom(ACCOUNT_ID, CLIENT_ID, CLIENT_SECRET)


@pytest.fixture
def zoomv2(requests_mock):
    """A Zoom (v2) connector with its OAuth handshake mocked."""
    requests_mock.post(ZOOM_AUTH_CALLBACK, json={"access_token": "fakeAccessToken"})
    return Zoom(ACCOUNT_ID, CLIENT_ID, CLIENT_SECRET, parsons_version="v2")
