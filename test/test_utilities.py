import unittest
import os
import pytest
import shutil
import datetime
from unittest import mock
from parsons import Table
from parsons.utilities.datetime import date_to_timestamp, parse_date
from parsons.utilities import files
from parsons.utilities import check_env
from parsons.utilities import json_format
from parsons.utilities import sql_helpers
from test.conftest import xfail_value_error


@pytest.mark.parametrize(
    ["date", "exp_ts"],
    [
        pytest.param("2018-12-13", 1544659200),
        pytest.param("2018-12-13T00:00:00-08:00", 1544688000),
        pytest.param("", None),
        pytest.param("2018-12-13 PST", None, marks=[xfail_value_error]),
    ],
)
def test_date_to_timestamp(date, exp_ts):
    assert date_to_timestamp(date) == exp_ts


def test_parse_date():
    # Test parsing an ISO8601 string
    expected = datetime.datetime(year=2020, month=1, day=1, tzinfo=datetime.timezone.utc)
    parsed = parse_date("2020-01-01T00:00:00.000 UTC")
    assert parsed == expected, parsed

    # Test parsing a unix timestamp
    parsed = parse_date(1577836800)
    assert parsed == expected, parsed

    # Test "parsing" a datetime object
    parsed = parse_date(expected)
    assert parsed == expected, parsed


#
# File utility tests (pytest-style)
#


def test_create_temp_file_for_path():
    temp_path = files.create_temp_file_for_path("some/file.gz")
    assert temp_path[-3:] == ".gz"


def test_create_temp_directory():
    temp_directory = files.create_temp_directory()
    test_file1 = f"{temp_directory}/test.txt"
    test_file2 = f"{temp_directory}/test2.txt"
    with open(test_file1, "w") as fh1, open(test_file2, "w") as fh2:
        fh1.write("TEST")
        fh2.write("TEST")

    assert files.has_data(test_file1)
    assert files.has_data(test_file2)

    files.cleanup_temp_directory(temp_directory)

    # Verify the temp file no longer exists
    with pytest.raises(FileNotFoundError):
        open(test_file1, "r")


def test_close_temp_file():
    temp = files.create_temp_file()
    files.close_temp_file(temp)

    # Verify the temp file no longer exists
    with pytest.raises(FileNotFoundError):
        open(temp, "r")


def test_is_gzip_path():
    assert files.is_gzip_path("some/file.gz")
    assert not files.is_gzip_path("some/file")
    assert not files.is_gzip_path("some/file.csv")


def test_suffix_for_compression_type():
    assert files.suffix_for_compression_type(None) == ""
    assert files.suffix_for_compression_type("") == ""
    assert files.suffix_for_compression_type("gzip") == ".gz"


def test_compression_type_for_path():
    assert files.compression_type_for_path("some/file") is None
    assert files.compression_type_for_path("some/file.csv") is None
    assert files.compression_type_for_path("some/file.csv.gz") == "gzip"


def test_empty_file():

    # Create fake files.
    os.mkdir("tmp")
    with open("tmp/empty.csv", "w+") as _:
        pass

    Table([["1"], ["a"]]).to_csv("tmp/full.csv")

    assert not files.has_data("tmp/empty.csv")
    assert files.has_data("tmp/full.csv")

    # Remove fake files and dir
    shutil.rmtree("tmp")


def test_json_format():
    assert json_format.arg_format("my_arg") == "myArg"


def test_remove_empty_keys():

    # Assert key removed when None
    test_dict = {"a": None, "b": 2}
    assert json_format.remove_empty_keys(test_dict) == {"b": 2}

    # Assert key not removed when None
    test_dict = {"a": 1, "b": 2}
    assert json_format.remove_empty_keys(test_dict) == {"a": 1, "b": 2}

    # Assert that a nested empty string is removed
    test_dict = {"a": "", "b": 2}
    assert json_format.remove_empty_keys(test_dict) == {"b": 2}


def test_redact_credentials():

    # Test with quotes, escape characters, and line breaks
    test_str = """COPY schema.tablename
    FROM 's3://bucket/path/to/file.csv'
    credentials  'aws_access_key_id=string-\\'escaped-quote;
    aws_secret_access_key='string-escape-char\\\\'
    MANIFEST"""

    test_result = """COPY schema.tablename
    FROM 's3://bucket/path/to/file.csv'
    CREDENTIALS REDACTED
    MANIFEST"""

    assert sql_helpers.redact_credentials(test_str) == test_result


class TestCheckEnv(unittest.TestCase):
    def test_environment_field(self):
        """Test check field"""
        result = check_env.check("PARAM", "param")
        self.assertEqual(result, "param")

    @mock.patch.dict(os.environ, {"PARAM": "env_param"})
    def test_environment_env(self):
        """Test check env"""
        result = check_env.check("PARAM", None)
        self.assertEqual(result, "env_param")

    @mock.patch.dict(os.environ, {"PARAM": "env_param"})
    def test_environment_field_env(self):
        """Test check field with env and field"""
        result = check_env.check("PARAM", "param")
        self.assertEqual(result, "param")

    def test_envrionment_error(self):
        """Test check env raises error"""
        with self.assertRaises(KeyError) as _:
            check_env.check("PARAM", None)
