import pytest

from parsons.solidarity_tech import SolidarityTech


@pytest.fixture
def st() -> SolidarityTech:
    return SolidarityTech(api_token="SOME_BEARER_KEY")
