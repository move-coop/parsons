from test.utils import mark_live_test

from parsons import Table

from contextlib import contextmanager
from requests.exceptions import HTTPError

# import json
import pytest

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
def cleanup_flag_id():
    def delete_flag_id(pdi, flag_id):
        pdi.delete_flag_id(flag_id)

    yield delete_flag_id


@pytest.fixture
def create_temp_flag_id():
    @contextmanager
    def temp_flag_id(pdi, my_flag_id=None):
        flag_id = my_flag_id or pdi.create_flag_id("amm", True)
        print(flag_id)

        yield flag_id

        if not my_flag_id:
            pdi.delete_flag_id(flag_id)

    yield temp_flag_id


#
# Tests
#


@mark_live_test
@pytest.mark.parametrize("limit", [None, 5, 15])
def test_get_flag_ids(live_pdi, limit):
    flag_ids = live_pdi.get_flag_ids(limit=limit)

    expected_columns = ["id", "flagId", "flagIdDescription", "compile", "isDefault"]
    expected_num_rows = limit or QA_NUM_FLAG_IDS

    assert isinstance(flag_ids, Table)
    assert flag_ids.columns == expected_columns
    assert flag_ids.num_rows == expected_num_rows


@mark_live_test
@pytest.mark.parametrize(
    "id",
    [
        pytest.param(QA_REAL_FLAG_ID),
        pytest.param(QA_INVALID_FLAG_ID, marks=[xfail_http_error]),
    ],
)
def test_get_flag_id(live_pdi, id):
    flag_id = live_pdi.get_flag_id(id)

    expected_keys = ["id", "flagId", "flagIdDescription", "compile", "isDefault"]

    assert isinstance(flag_id, dict)
    assert list(flag_id.keys()) == expected_keys


@mark_live_test
@pytest.mark.parametrize(
    ["flag_id", "is_default"],
    [
        pytest.param(None, True, marks=[xfail_http_error]),
        pytest.param("amm", None, marks=[xfail_http_error]),
        pytest.param("amm", True),
    ],
)
def test_create_flag_id(live_pdi, cleanup_flag_id, flag_id, is_default):
    flag_id = live_pdi.create_flag_id(flag_id, is_default)

    cleanup_flag_id(live_pdi, flag_id)


@mark_live_test
@pytest.mark.parametrize(
    ["my_flag_id"],
    [
        pytest.param(None),
        pytest.param(QA_INVALID_FLAG_ID),
        pytest.param(QA_MALFORMED_FLAG_ID, marks=[xfail_http_error]),
    ],
)
def test_delete_flag_id(live_pdi, create_temp_flag_id, my_flag_id):
    with create_temp_flag_id(live_pdi, my_flag_id) as flag_id:
        did_delete = live_pdi.delete_flag_id(flag_id)

    assert did_delete


@mark_live_test
@pytest.mark.parametrize(
    ["my_flag_id"],
    [
        pytest.param(None),
        pytest.param(QA_INVALID_FLAG_ID, marks=[xfail_http_error]),
        pytest.param(QA_MALFORMED_FLAG_ID, marks=[xfail_http_error]),
    ],
)
def test_update_flag_id(live_pdi, create_temp_flag_id, my_flag_id):
    with create_temp_flag_id(live_pdi, my_flag_id) as flag_id:
        # flag initial state:
        # {"id":flag_id,"flagId":"amm","flagIdDescription":null,"compile":"","isDefault":false}  # noqa
        id = live_pdi.update_flag_id(flag_id, "bnh", True)
        assert id == flag_id

        expected_dict = {
            "id": flag_id,
            "flagId": "bnh",
            "flagIdDescription": None,
            "compile": "",
            "isDefault": True,
        }

        flag_id_dict = live_pdi.get_flag_id(flag_id)

        assert expected_dict == flag_id_dict
