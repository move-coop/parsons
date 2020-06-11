import pytest
import os
from parsons.etl import Table
from parsons.sftp import SFTP
from parsons.utilities import files
from test.utils import mark_live_test, assert_matching_tables
from test.fixtures import simple_table, simple_csv_path, simple_compressed_csv_path

#
# Fixtures and constants
#

REMOTE_DIR = 'parsons-test'
REMOTE_CSV = 'test.csv'
REMOTE_CSV_PATH = f'{REMOTE_DIR}/{REMOTE_CSV}'
REMOTE_COMPRESSED_CSV = 'test.csv.gz'
REMOTE_COMPRESSED_CSV_PATH = f'{REMOTE_DIR}/{REMOTE_COMPRESSED_CSV}'

@pytest.fixture
def live_sftp(simple_table, simple_csv_path, simple_compressed_csv_path):
    # Generate a live SFTP connection based on these env vars
    host = os.environ['SFTP_HOST']
    username = os.environ['SFTP_USERNAME']
    password = os.environ['SFTP_PASSWORD']

    sftp = SFTP(host, username, password)

    # Add a test directory and test files
    sftp.make_directory(REMOTE_DIR)
    sftp.put_file(simple_csv_path, REMOTE_CSV_PATH)
    sftp.put_file(simple_compressed_csv_path, REMOTE_COMPRESSED_CSV_PATH)

    yield sftp

    # Cleanup after test
    sftp.remove_file(REMOTE_CSV_PATH)
    sftp.remove_file(REMOTE_COMPRESSED_CSV_PATH)
    sftp.remove_directory(REMOTE_DIR)

#
# Tests
#

def test_credential_validation():
    with pytest.raises(ValueError):
        SFTP(host=None, username=None, password=None)

    with pytest.raises(ValueError):
        SFTP(host=None, username='sam', password='abc123')

@mark_live_test
def test_list_non_existent_directory(live_sftp):
    with pytest.raises(FileNotFoundError):
        file_list = live_sftp.list_directory('abc123')

@mark_live_test
def test_list_directory_with_files(live_sftp):
    file_list = live_sftp.list_directory(REMOTE_DIR)
    assert file_list == [REMOTE_COMPRESSED_CSV, REMOTE_CSV]

@mark_live_test
def test_get_non_existent_file(live_sftp):
    with pytest.raises(FileNotFoundError):
        live_sftp.get_file('abc123')

# Helper function
def assert_file_matches_table(local_path, table):
    downloaded_tbl = Table.from_csv(local_path)
    assert_matching_tables(table, downloaded_tbl)

@mark_live_test
def test_get_file(live_sftp, simple_table):
    local_path = files.create_temp_file()
    live_sftp.get_file(REMOTE_CSV_PATH, local_path=local_path)
    assert_file_matches_table(local_path, simple_table)

@mark_live_test
def test_get_table(live_sftp, simple_table):
    local_path = files.create_temp_file()
    tbl = live_sftp.get_table(REMOTE_CSV_PATH)
    assert_matching_tables(tbl, simple_table)

@mark_live_test
def test_get_temp_file(live_sftp, simple_table):
    local_path = live_sftp.get_file(REMOTE_CSV_PATH)
    assert_file_matches_table(local_path, simple_table)

@mark_live_test
@pytest.mark.parametrize('compression', [None, 'gzip'])
def test_table_to_sftp_csv(live_sftp, simple_table, compression):
    host = os.environ['SFTP_HOST']
    username = os.environ['SFTP_USERNAME']
    password = os.environ['SFTP_PASSWORD']
    remote_path = f'{REMOTE_DIR}/test_to_sftp.csv'
    if compression == 'gzip':
        remote_path += '.gz'
    simple_table.to_sftp_csv(remote_path, host, username, password, compression=compression)

    local_path = live_sftp.get_file(remote_path)
    assert_file_matches_table(local_path, simple_table)

    # Cleanup
    live_sftp.remove_file(remote_path)


# Stuff that is tested by the live_sftp fixture, so no need to test explicitly:
# test_make_directory
# test_put_file
# test_put_file_compressed
# def test_remove_file
# def test_remove_directory
