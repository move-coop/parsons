import pytest

from parsons import Bloomerang


@pytest.fixture
def bloomerang():
    """Create a fresh Bloomerang connector authenticated with a fake API key."""
    return Bloomerang(api_key="test_key")
