import pytest

from parsons import MobilizeAmerica


@pytest.fixture
def mobilize() -> MobilizeAmerica:
    """A MobilizeAmerica connector (construction makes no request)."""
    return MobilizeAmerica(api_key="test_password")
