import os
from unittest import mock

import pytest

from parsons.solidarity_tech.solidarity_tech import SolidarityTech

PLACEHOLDER_TOKEN = "SOME_API_KEY"


def test_init_with_arg() -> None:
    st = SolidarityTech(api_token=PLACEHOLDER_TOKEN)
    assert st.api_token == PLACEHOLDER_TOKEN
    assert st.headers.get("authorization") == f"Bearer {PLACEHOLDER_TOKEN}"


@mock.patch.dict(os.environ, {"SOLIDARITY_TECH_TOKEN": PLACEHOLDER_TOKEN})
def test_init_with_env() -> None:
    st = SolidarityTech()
    assert st.api_token == PLACEHOLDER_TOKEN
    assert st.headers.get("authorization") == f"Bearer {PLACEHOLDER_TOKEN}"


def test_init_with_no_api_token() -> None:
    with pytest.raises(KeyError, match="No 'SOLIDARITY_TECH_TOKEN' found."):
        SolidarityTech()
