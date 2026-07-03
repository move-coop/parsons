import pytest

from parsons import SMTP
from test.test_smtp.fakes import FakeSMTPConnection


@pytest.fixture
def conn() -> FakeSMTPConnection:
    """A fake SMTP connection that records the message it was asked to send."""
    return FakeSMTPConnection()


@pytest.fixture
def smtp(conn) -> SMTP:
    """
    An SMTP connector wired to a fake connection.

    SMTP speaks a stateful protocol (connect, send, quit), so the boundary we do
    not own is the connection object. We build the connector with fake
    credentials and inject the fake connection instead of mocking method by
    method.
    """
    client = SMTP("fake.example.com", username="fake", password="fake")
    client.conn = conn
    return client
