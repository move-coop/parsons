import pytest

from parsons import RockTheVote

PARTNER_ID = "1"
PARTNER_API_KEY = "abcd"


@pytest.fixture
def rtv() -> RockTheVote:
    """A RockTheVote connector with fake credentials (construction makes no request)."""
    return RockTheVote(partner_id=PARTNER_ID, partner_api_key=PARTNER_API_KEY)
