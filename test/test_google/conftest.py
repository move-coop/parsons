import pytest

from parsons import GoogleCivic
from parsons.google.google_admin import GoogleAdmin


class MockGoogleAdmin(GoogleAdmin):
    """A GoogleAdmin connector whose client is replaced with a mock.

    Bypasses the real credential loading in ``GoogleAdmin.__init__`` so that
    tests can drive the connector against a mocked ``client``.
    """

    def __init__(self):
        # ``client`` is assigned by the fixture using the ``mocker`` fixture.
        pass


@pytest.fixture
def google_admin(mocker):
    """Provide a GoogleAdmin connector with a mocked client."""
    admin = MockGoogleAdmin()
    admin.client = mocker.MagicMock()
    return admin


@pytest.fixture
def googlecivic():
    """Provide a GoogleCivic connector authenticated with a fake API key."""
    return GoogleCivic(api_key="FAKEKEY")
