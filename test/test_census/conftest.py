import pytest

from parsons import Census

MOCK_API_KEY = "mock_api_key"


@pytest.fixture
def census():
    """Provides a Census connector built with fake credentials."""
    return Census(api_key=MOCK_API_KEY)
