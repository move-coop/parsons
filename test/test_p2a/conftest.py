import pytest

from parsons import Phone2Action


@pytest.fixture
def p2a() -> Phone2Action:
    """A Phone2Action connector with fake credentials (construction makes no request)."""
    return Phone2Action(app_id="an_id", app_key="app_key")
