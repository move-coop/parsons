import pytest

from parsons import Airtable

BASE_KEY = "BASEKEY"
TABLE_NAME = "TABLENAME"
BASE_URI = f"https://api.airtable.com/v0/{BASE_KEY}/{TABLE_NAME}"


@pytest.fixture
def base_uri() -> str:
    """The Airtable REST endpoint the connector calls for this base/table."""
    return BASE_URI


@pytest.fixture
def airtable() -> Airtable:
    """
    An Airtable connector wired to a fake base/table.

    The connector wraps the ``pyairtable`` SDK, which issues its HTTP requests
    through ``requests`` — so tests mock at the HTTP layer with the
    ``requests_mock`` fixture. Constructing the connector makes no network call,
    so no mock is needed here.
    """
    return Airtable(
        base_key=BASE_KEY,
        table_name=TABLE_NAME,
        personal_access_token="fake-personal-access-token",
    )
