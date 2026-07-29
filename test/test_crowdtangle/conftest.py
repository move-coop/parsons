import pytest

from parsons import CrowdTangle


@pytest.fixture
def crowdtangle() -> CrowdTangle:
    """A CrowdTangle connector with a fake key (construction makes no request)."""
    return CrowdTangle("FAKE_KEY")
