import os
from unittest import mock

import pytest

from parsons.solidarity_tech.solidarity_tech import SolidarityTech

TOKEN_ENV_NAME = "SOLIDARITY_TECH_BEARER_KEY"
TOKEN_PLACEHOLDER = "SOME_BEARER_KEY"


def test_init_with_arg() -> None:
    st = SolidarityTech(api_token=TOKEN_PLACEHOLDER)
    assert st.api_token == TOKEN_PLACEHOLDER
    assert st.headers.get("authorization") == f"Bearer {TOKEN_PLACEHOLDER}"


@mock.patch.dict(os.environ, {TOKEN_ENV_NAME: TOKEN_PLACEHOLDER})
def test_init_with_env() -> None:
    st = SolidarityTech()
    assert st.api_token == TOKEN_PLACEHOLDER
    assert st.headers.get("authorization") == f"Bearer {TOKEN_PLACEHOLDER}"


def test_init_with_no_api_token() -> None:
    with pytest.raises(KeyError, match="No '{TOKEN_ENV_NAME}' found."):
        SolidarityTech()
