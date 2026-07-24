import pytest

from parsons import Community

CLIENT_ID = "someuuid"
CLIENT_TOKEN = "somesecret"
URI = f"https://faketestingurl.com/{CLIENT_ID}"


@pytest.fixture
def uri() -> str:
    return URI


@pytest.fixture
def client_id() -> str:
    return CLIENT_ID


@pytest.fixture
def client_token() -> str:
    return CLIENT_TOKEN


@pytest.fixture
def community() -> Community:
    """A Community connector with fake credentials (construction makes no request)."""
    return Community(CLIENT_ID, CLIENT_TOKEN, URI)
