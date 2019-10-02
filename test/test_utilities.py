import unittest
import os
import pytest
from unittest import mock
from parsons.utilities import date_convert
from parsons.utilities import files
from parsons.utilities import check_env
from parsons.utilities import json_format


"""
# Does not work locally due to some UTC issues, but works on CircleCI. Commenting
# out for the time being.

class TestDateConvert(unittest.TestCase):

    def test_date_convert(self):

        self.assertEqual(date_convert.iso_to_unix('2018-12-13'), 1544659200)
"""

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

def test_json_format():
    assert json_format.arg_format('my_arg') == 'myArg'

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

