from __future__ import annotations

import pytest
import requests

from parsons.solidarity_tech import SolidarityTech
from parsons.solidarity_tech.auth import SolidarityTechAuth

TOKEN_ENV_NAME = "SOLIDARITY_TECH_BEARER_KEY"
TOKEN_PLACEHOLDER = "SOME_BEARER_KEY"


def test_init_with_arg() -> None:
    """Set api_token property and header when initialized via an argument."""
    st = SolidarityTech(api_token=TOKEN_PLACEHOLDER)
    assert isinstance(st.api.auth, SolidarityTechAuth)

    req = requests.Request("GET", url="https://api.example.com", auth=st.api.auth)
    req = req.prepare()
    assert req.headers.get("authorization") == f"Bearer {TOKEN_PLACEHOLDER}"


def test_init_with_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set api_token property and header when initialized via environment variable."""
    with monkeypatch.context() as m:
        m.setenv(TOKEN_ENV_NAME, TOKEN_PLACEHOLDER)
        st = SolidarityTech()
    assert isinstance(st.api.auth, SolidarityTechAuth)

    req = requests.Request("GET", url="https://api.example.com", auth=st.api.auth)
    req = req.prepare()
    assert req.headers.get("authorization") == f"Bearer {TOKEN_PLACEHOLDER}"


def test_init_with_no_api_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raise :class:`KeyError` when no API token is provided and the environment variable is not set."""
    with monkeypatch.context() as m:
        m.delenv(TOKEN_ENV_NAME, raising=False)
        with pytest.raises(KeyError, match=f"No '{TOKEN_ENV_NAME}' found."):
            SolidarityTech()


def test_init_api_url(st: SolidarityTech) -> None:
    """Set api_url property."""
    assert st.api_url == "https://api.solidarity.tech/v1/"
