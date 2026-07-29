import pytest

from parsons import Mailchimp

API_KEY = "mykey-us00"


@pytest.fixture
def mailchimp() -> Mailchimp:
    """A Mailchimp connector with a fake key (construction makes no request)."""
    return Mailchimp(API_KEY)
