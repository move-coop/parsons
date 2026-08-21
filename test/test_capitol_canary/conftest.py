import pytest

from parsons import CapitolCanary


@pytest.fixture
def cc() -> CapitolCanary:
    """A CapitolCanary connector with fake credentials (construction makes no request)."""
    return CapitolCanary(app_id="an_id", app_key="app_key")
