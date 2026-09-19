"""Test fixtures for the SolidarityTech client."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest

from parsons.solidarity_tech import SolidarityTech

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture
def st() -> SolidarityTech:
    """Create a SolidarityTech instance with a placeholder api key."""
    api_key = (
        os.environ.get("SOLIDARITY_TECH_BEARER_KEY")
        if "SOLIDARITY_TECH_BEARER_KEY" in os.environ
        else "SOME_BEARER_KEY"
    )
    return SolidarityTech(api_token=api_key)


@pytest.fixture
def format_ts() -> Callable[[int, int], str]:
    """Fixturize format_ts function to format a string in SolidarityTech's timestamp format."""

    def format_ts(ts: int, tz_offset: int) -> str:
        """Format a timestamp as a string in the format 'YYYY-MM-DDTHH:MM:SS.000Z'."""
        tz = timezone(timedelta(hours=tz_offset))
        dt = datetime.fromtimestamp(ts, timezone.utc).astimezone(tz)
        s = dt.strftime("%Y-%m-%dT%H:%M:%S.000%z")
        return f"{s[:-2]}:{s[-2:]}"

    return format_ts
