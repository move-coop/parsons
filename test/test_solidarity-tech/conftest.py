from __future__ import annotations

import pytest

from parsons.solidarity_tech import SolidarityTech


@pytest.fixture
def st() -> SolidarityTech:
    """Create a SolidarityTech instance with a placeholder api key."""
    return SolidarityTech(api_token="SOME_BEARER_KEY")
