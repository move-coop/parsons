import unittest
import os
import pytest
import shutil
from unittest import mock
from parsons.etl.table import Table
from parsons.utilities import date_convert
from parsons.utilities import files
from parsons.utilities import check_env
from parsons.utilities import json_format
from test.conftest import xfail_value_error


@pytest.mark.parametrize(
    ["date", "exp_ts"],
    [pytest.param("2018-12-13", 1544659200),
     pytest.param("2018-12-13T00:00:00-08:00", 1544688000),
     pytest.param("", None),
     pytest.param("2018-12-13 PST", None, marks=[xfail_value_error]),
     ])
def test_date_convert(date, exp_ts):
    assert date_convert.iso_to_unix(date) == exp_ts

#
# File utility tests (pytest-style)
#


def test_create_temp_file_for_path():
    temp_path = files.create_temp_file_for_path('some/file.gz')
    assert temp_path[-3:] == '.gz'

def test_close_temp_file():
    temp = files.create_temp_file()
    files.close_temp_file(temp)

    # Verify the temp file no longer exists
    with pytest.raises(FileNotFoundError):
        open(temp, 'r')


def test_is_gzip_path():
    assert files.is_gzip_path('some/file.gz')
    assert not files.is_gzip_path('some/file')
    assert not files.is_gzip_path('some/file.csv')


def test_suffix_for_compression_type():
    assert files.suffix_for_compression_type(None) == ''
    assert files.suffix_for_compression_type('') == ''
    assert files.suffix_for_compression_type('gzip') == '.gz'


def test_compression_type_for_path():
    assert files.compression_type_for_path('some/file') == None
    assert files.compression_type_for_path('some/file.csv') == None
    assert files.compression_type_for_path('some/file.csv.gz') == 'gzip'

def test_empty_file():

    # Create fake files.
    os.mkdir('tmp')
    with open('tmp/empty.csv', 'w+') as f:
        pass
    Table([['1'],['a']]).to_csv('tmp/full.csv')

    assert files.has_data('tmp/empty.csv') == False
    assert files.has_data('tmp/full.csv') == True

    # Remove fake files and dir
    shutil.rmtree('tmp')

def test_json_format():
    assert json_format.arg_format('my_arg') == 'myArg'

def test_remove_empty_keys():

    # Assert key removed when None
    test_dict = {'a': None, 'b': 2}
    assert json_format.remove_empty_keys(test_dict) == {'b': 2}

    # Assert key not removed when None
    test_dict = {'a': 1, 'b': 2}
    assert json_format.remove_empty_keys(test_dict) == {'a': 1, 'b': 2}

    # Assert that a nested empty string is removed
    test_dict = {'a': '', 'b': 2}
    assert json_format.remove_empty_keys(test_dict) ==  {'b': 2}

class TestCheckEnv(unittest.TestCase):

    def test_environment_field(self):
        """Test check field"""
        result = check_env.check('PARAM', 'param')
        self.assertEqual(result, 'param')

    @mock.patch.dict(os.environ, {'PARAM': 'env_param'})
    def test_environment_env(self):
        """Test check env"""
        result = check_env.check('PARAM', None)
        self.assertEqual(result, 'env_param')

    @mock.patch.dict(os.environ, {'PARAM': 'env_param'})
    def test_environment_field_env(self):
        """Test check field with env and field"""
        result = check_env.check('PARAM', 'param')
        self.assertEqual(result, 'param')

    def test_envrionment_error(self):
        """Test check env raises error"""
        with self.assertRaises(KeyError) as context:
            check_env.check('PARAM', None)
