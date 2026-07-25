import json

import pytest

from parsons.quickbooks.quickbookstime import QuickBooksTime


@pytest.fixture
def quickbooks() -> QuickBooksTime:
    """A QuickBooksTime connector with a fake token (construction makes no request)."""
    qb = QuickBooksTime(token="abc123")
    qb.url = "https://rest.tsheets.com/api/v1/"
    return qb


@pytest.fixture
def load(shared_datadir):
    """Load a canned QuickBooks Time response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
