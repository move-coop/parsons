import pytest

from parsons import Copper


@pytest.fixture
def copper() -> Copper:
    """A Copper connector with fake credentials (construction makes no request)."""
    return Copper("usr@losr.fake", "key")


@pytest.fixture(autouse=True)
def _no_sleep(mocker):
    """``paginate_request`` sleeps 1s per page to respect rate limits; skip it in tests."""
    mocker.patch("parsons.copper.copper.time.sleep")
