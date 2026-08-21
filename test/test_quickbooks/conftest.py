import pytest

from parsons.quickbooks.quickbookstime import QuickBooksTime


@pytest.fixture
def quickbooks() -> QuickBooksTime:
    """A QuickBooksTime connector with a fake token (construction makes no request)."""
    qb = QuickBooksTime(token="abc123")
    qb.url = "https://rest.tsheets.com/api/v1/"
    return qb
