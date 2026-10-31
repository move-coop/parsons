from collections.abc import Callable, Generator
from contextlib import contextmanager

# import json
import pytest
from requests.exceptions import HTTPError

from parsons import PDI, Table

#
# Fixtures and constants
#

# Set these to be valid for a qa account

# get_flag_ids
QA_NUM_FLAG_IDS = 34

# get_flag_id
QA_REAL_FLAG_ID = "RtK8WQc4uTnuJYGCHMDpmA=="
QA_INVALID_FLAG_ID = "jE0muNuPKfSTg8hTen10kA=="
QA_MALFORMED_FLAG_ID = QA_INVALID_FLAG_ID[:-1]

# create a mark that expects a failure from HTTPError
xfail_http_error = pytest.mark.xfail(raises=HTTPError, strict=True)


@pytest.fixture
def cleanup_flag_id() -> Callable[[PDI, str], None]:
    def delete_flag_id(pdi: PDI, flag_id: str) -> None:
        pdi.delete_flag_id(flag_id)

    return delete_flag_id


@pytest.fixture
def create_temp_flag_id():
    @contextmanager
    def temp_flag_id(pdi: PDI, my_flag_id: str | None = None) -> Generator[str, None, None]:
        flag_id = my_flag_id or pdi.create_flag_id("AMM", is_default=True)
        print(flag_id)

        yield flag_id

        if not my_flag_id:
            pdi.delete_flag_id(flag_id)

    return temp_flag_id


#
# Tests
#


@pytest.mark.live
@pytest.mark.parametrize("limit", [None, 5, 15])
def test_get_flag_ids(live_pdi: PDI, limit):
    flag_ids = live_pdi.get_flag_ids(limit=limit)

    expected_columns = ["id", "flagId", "flagIdDescription", "compile", "isDefault"]
    expected_num_rows = limit or QA_NUM_FLAG_IDS

    assert isinstance(flag_ids, Table)
    assert flag_ids.columns == expected_columns
    assert flag_ids.num_rows == expected_num_rows


@pytest.mark.live
@pytest.mark.parametrize(
    "flag_id",
    [
        pytest.param(QA_REAL_FLAG_ID),
        pytest.param(QA_INVALID_FLAG_ID, marks=[xfail_http_error]),
    ],
)
def test_get_flag_id(live_pdi: PDI, flag_id: str):
    flag_id = live_pdi.get_flag_id(flag_id)

    expected_keys = ["id", "flagId", "flagIdDescription", "compile", "isDefault"]

    assert isinstance(flag_id, dict)
    assert list(flag_id.keys()) == expected_keys


@pytest.mark.live
@pytest.mark.parametrize(
    ("flag_id", "is_default"),
    [
        pytest.param(None, True, marks=[xfail_http_error]),
        pytest.param("AMM", None, marks=[xfail_http_error]),
        pytest.param("AMM", True),
    ],
)
def test_create_flag_id(
    live_pdi: PDI,
    cleanup_flag_id: Callable[[PDI, str], None],
    flag_id: str | None,
    is_default: bool | None,
):
    flag_id = live_pdi.create_flag_id(flag_id, is_default)

    cleanup_flag_id(live_pdi, flag_id)


@pytest.mark.live
@pytest.mark.parametrize(
    "my_flag_id",
    [
        pytest.param(None),
        pytest.param(QA_INVALID_FLAG_ID),
        pytest.param(QA_MALFORMED_FLAG_ID, marks=[xfail_http_error]),
    ],
)
def test_delete_flag_id(live_pdi: PDI, create_temp_flag_id, my_flag_id: str | None):
    with create_temp_flag_id(live_pdi, my_flag_id) as temp_flag_id:
        assert live_pdi.delete_flag_id(temp_flag_id)


@pytest.mark.live
@pytest.mark.parametrize(
    "my_flag_id",
    [
        pytest.param(None),
        pytest.param(QA_INVALID_FLAG_ID, marks=[xfail_http_error]),
        pytest.param(QA_MALFORMED_FLAG_ID, marks=[xfail_http_error]),
    ],
)
def test_update_flag_id(live_pdi: PDI, create_temp_flag_id, my_flag_id: str | None):
    with create_temp_flag_id(live_pdi, my_flag_id) as temp_flag_id:
        # flag initial state:
        # {"id":flag_id, "flagId":"amm", "flagIdDescription":null, "compile":"", "isDefault":false}
        assert live_pdi.update_flag_id(temp_flag_id, "BNH", is_default=True) == temp_flag_id

        expected_dict = {
            "id": temp_flag_id,
            "flagId": "bnh",
            "flagIdDescription": None,
            "compile": "",
            "isDefault": True,
        }

        assert live_pdi.get_flag_id(temp_flag_id) == expected_dict
