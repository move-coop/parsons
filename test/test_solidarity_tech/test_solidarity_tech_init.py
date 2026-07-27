import os
from unittest import mock

import pytest

from parsons.solidarity_tech.solidarity_tech import SolidarityTech


def test_init_with_arg() -> None:
    SolidarityTech(api_token="SOME_API_KEY")


@mock.patch.dict(os.environ, {"SOLIDARITY_TECH_TOKEN": "SOME_API_KEY"})
def test_init_with_env() -> None:
    SolidarityTech()


def test_init_with_no_api_token() -> None:
    with pytest.raises(KeyError, match="No 'SOLIDARITY_TECH_TOKEN' found."):
        SolidarityTech()
