"""Test fixtures for the SolidarityTech client."""

from __future__ import annotations

import os

import pytest

from parsons.solidarity_tech import SolidarityTech


@pytest.fixture
def st() -> SolidarityTech:
    """Create a SolidarityTech instance with a placeholder api key."""
    api_key = (
        os.environ.get("SOLIDARITY_TECH_BEARER_KEY")
        if "SOLIDARITY_TECH_BEARER_KEY" in os.environ
        else "SOME_BEARER_KEY"
    )
    return SolidarityTech(api_token=api_key)
