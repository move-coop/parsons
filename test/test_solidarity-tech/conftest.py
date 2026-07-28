import pytest

from parsons.solidarity_tech.solidarity_tech import SolidarityTech


@pytest.fixture
def st() -> SolidarityTech:
    return SolidarityTech(api_token="SOME_API_KEY")
