from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from parsons.solidarity_tech import SolidarityTech

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


TOKEN_ENV_NAME = "SOLIDARITY_TECH_BEARER_KEY"
TOKEN_PLACEHOLDER = "SOME_BEARER_KEY"


def test_init_with_arg() -> None:
    """Set api_token property and header when initialized via an argument."""
    st = SolidarityTech(api_token=TOKEN_PLACEHOLDER)
    assert st.api_token == TOKEN_PLACEHOLDER
    assert st.headers.get("authorization") == f"Bearer {TOKEN_PLACEHOLDER}"


def test_init_with_env(mocker: MockerFixture) -> None:
    """Set api_token property and header when initialized via environment variable."""
    mocker.patch.dict(os.environ, {TOKEN_ENV_NAME: TOKEN_PLACEHOLDER})
    st = SolidarityTech()
    assert st.api_token == TOKEN_PLACEHOLDER
    assert st.headers.get("authorization") == f"Bearer {TOKEN_PLACEHOLDER}"


def test_init_with_no_api_token() -> None:
    """Raise :class:`KeyError` when no API token is provided and the environment variable is not set."""
    with pytest.raises(KeyError, match=f"No '{TOKEN_ENV_NAME}' found."):
        SolidarityTech()


def test_init_api_url(st: SolidarityTech) -> None:
    """Set api_url property."""
    assert st.api_url == "https://api.solidarity.tech/v1/"
