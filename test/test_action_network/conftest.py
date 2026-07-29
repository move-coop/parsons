import pytest

from parsons.action_network import ActionNetwork


@pytest.fixture
def an() -> ActionNetwork:
    """An ActionNetwork connector with a fake token (construction makes no request)."""
    return ActionNetwork("fake_key")
