import pytest

from parsons import VAN

FAKE_API_KEY = "SOME_KEY"


@pytest.fixture
def van():
    """A VAN connector backed by the MyVoters database and a fake API key."""
    return VAN(FAKE_API_KEY, db="MyVoters")


@pytest.fixture
def van_everyaction():
    """A VAN connector backed by the EveryAction database and a fake API key."""
    return VAN(FAKE_API_KEY, db="EveryAction")
