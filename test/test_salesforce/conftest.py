import pytest

from parsons import Salesforce


@pytest.fixture
def salesforce(mocker) -> Salesforce:
    """
    A Salesforce connector with its SDK client replaced by a mock.

    The connector wraps the ``simple-salesforce`` client, so the boundary we do
    not own is that client object. We build the connector with fake credentials
    (no network call happens at construction — the real client is created lazily)
    and swap ``_client`` for a ``MagicMock``. Each test programs the specific
    client methods it exercises.
    """
    sf = Salesforce(
        username="fake-user",
        password="fake-password",
        security_token="fake-token",
    )
    sf._client = mocker.MagicMock()
    return sf
