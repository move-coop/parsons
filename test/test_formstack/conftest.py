import pytest

from parsons import Formstack


@pytest.fixture
def formstack() -> Formstack:
    """A Formstack connector with a fake token (construction makes no request)."""
    return Formstack(api_token="token")
