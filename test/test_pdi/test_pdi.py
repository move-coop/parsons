from test.utils import mark_live_test
from parsons import PDI

import pytest
import os


#
# Fixtures and constants
#
def remove_from_env(*env_vars):
    for var in env_vars:
        try:
            del os.environ[var]
        except KeyError:
            pass


#
# Tests
#


# Need to provide environment variables
# PDI_USERNAME, PDI_PASSWORD, PDI_API_TOKEN
@mark_live_test
def test_connection():
    PDI(qa_url=True)


@pytest.mark.parametrize(
    ["username", "password", "api_token"],
    [
        (None, None, None),
        (None, "pass", "token"),
        ("user", None, "token"),
        ("user", "pass", None),
    ],
)
def test_init_error(username, password, api_token):
    remove_from_env("PDI_USERNAME", "PDI_PASSWORD", "PDI_API_TOKEN")
    with pytest.raises(KeyError):
        PDI(username, password, api_token)


@pytest.mark.parametrize(
    ["obj", "exp_obj"],
    [
        ({"a": "a", "b": None, "c": "c"}, {"a": "a", "c": "c"}),
        (
            [{"a": "a", "b": None, "c": "c"}, {"a": "a", "c": None}],
            [{"a": "a", "c": "c"}, {"a": "a"}],
        ),
        ("string", "string"),
    ],
)
def test_clean_dict(mock_pdi, obj, exp_obj):
    assert mock_pdi._clean_dict(obj) == exp_obj
