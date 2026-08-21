import pytest

from parsons import ActBlue

TEST_CLIENT_UUID = "someuuid"
TEST_CLIENT_SECRET = "somesecret"
TEST_URI = "https://faketestingurl.com/example"


@pytest.fixture
def actblue():
    """Build an ActBlue connector with fake credentials."""
    return ActBlue(TEST_CLIENT_UUID, TEST_CLIENT_SECRET, TEST_URI)
