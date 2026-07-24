import pytest

from parsons import TurboVote

USERNAME = "usr"
PASSWORD = "pwd"
SUBDOMAIN = "myorg"


@pytest.fixture
def turbovote() -> TurboVote:
    """A TurboVote connector with fake credentials (construction makes no request)."""
    return TurboVote(USERNAME, PASSWORD, SUBDOMAIN)
