import pytest

from parsons import Twilio


@pytest.fixture
def twilio(mocker):
    """A Twilio connector with its ``twilio.rest.Client`` mocked.

    Twilio wraps a ``twilio.rest.Client`` (``self.client``); that client is the external
    boundary, so we patch it at its import site and program ``twilio.client.<...>``
    per test.
    """
    mocker.patch("parsons.twilio.twilio.Client")
    return Twilio(account_sid="FAKESID", auth_token="FAKETOKEN")
