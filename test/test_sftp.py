import pytest
import os
import paramiko
from contextlib import contextmanager
from copy import deepcopy
from unittest.mock import MagicMock, patch, call
from parsons import Table, SFTP
from parsons.utilities import files as file_util
from test.utils import mark_live_test, assert_matching_tables
from test.fixtures import (  # noqa: F401
    simple_table,
    simple_csv_path,
    simple_compressed_csv_path,
)

#
# Fixtures and constants
#

REMOTE_DIR, CSV, COMPRESSED_CSV, EMPTY, SUBDIR_A, SUBDIR_B, CSV_A, CSV_B = [
    "parsons_test",
    "test.csv",
    "test.csv.gz",
    "empty",
    "subdir_a",
    "subdir_b",
    "test_a.csv",
    "test_b.csv",
]

CSV_PATH, COMPRESSED_CSV_PATH, EMPTY_PATH, SUBDIR_A_PATH, SUBDIR_B_PATH = [
    f"{REMOTE_DIR}/{content}" for content in (CSV, COMPRESSED_CSV, EMPTY, SUBDIR_A, SUBDIR_B)
]

CSV_A_PATH, CSV_B_PATH = [
    f"{d}/{content}" for d, content in ((SUBDIR_A_PATH, CSV_B), (SUBDIR_B_PATH, CSV_A))
]

FILE_PATHS = [CSV_PATH, COMPRESSED_CSV_PATH, CSV_A_PATH, CSV_B_PATH]
DIR_PATHS = [REMOTE_DIR, EMPTY_PATH, SUBDIR_A_PATH, SUBDIR_B_PATH]


def sup(sftp, simple_csv_path, simple_compressed_csv_path):  # noqa: F811
    # The setup function creates remote directories and files needed for live tests
    for remote_dir in DIR_PATHS:
        sftp.make_directory(remote_dir)

    for remote_file in FILE_PATHS:
        fixture = simple_compressed_csv_path if "gz" in remote_file else simple_csv_path
        sftp.put_file(fixture, remote_file)


def cleanup(sftp):
    for f in FILE_PATHS:
        sftp.remove_file(f)
    for remote_dir in reversed(DIR_PATHS):
        sftp.remove_directory(remote_dir)


def generate_live_sftp_connection():
    host = os.environ["SFTP_HOST"]
    username = os.environ["SFTP_USERNAME"]
    password = os.environ["SFTP_PASSWORD"]
    return SFTP(host, username, password)


@pytest.fixture
def live_sftp(simple_csv_path, simple_compressed_csv_path, simple_table):  # noqa: F811
    sftp = generate_live_sftp_connection()
    sup(sftp, simple_csv_path, simple_compressed_csv_path)
    yield sftp
    cleanup(sftp)


# This second live_sftp fixture is used for test_get_files so that files are never downloaded and
# mocks can be inspected.
@pytest.fixture
def live_sftp_with_mocked_get(simple_csv_path, simple_compressed_csv_path):  # noqa: F811
    SFTP_with_mocked_get = deepcopy(SFTP)

    # The names of temp files are long arbitrary strings. This makes them predictable.
    def rv(magic_mock):
        return ["foo", "bar", "baz"][magic_mock.call_count]

    get = MagicMock()
    create_temp_file_for_path = MagicMock()
    create_temp_file_for_path.return_value = rv(create_temp_file_for_path)

    # The following two methods are identical to their cognates in the SFTP class, but they
    # substitue a mock for `conn.get` and `files.create_temp_file_for_path`, respectively.
    @contextmanager
    def create_connection(self):
        transport = paramiko.Transport((self.host, self.port))
        pkey = None
        if self.rsa_private_key_file:
            pkey = paramiko.RSAKey.from_private_key_file(self.rsa_private_key_file)

        transport.connect(username=self.username, password=self.password, pkey=pkey)
        conn = paramiko.SFTPClient.from_transport(transport)
        conn.get = get
        yield conn
        conn.close()
        transport.close()

    def get_file(self, remote_path, local_path=None, connection=None):

        if not local_path:
            local_path = create_temp_file_for_path(remote_path)

        if connection:
            connection.get(remote_path, local_path)
        else:
            with self.create_connection() as connection:
                connection.get(remote_path, local_path)

        return local_path

    SFTP_with_mocked_get.create_connection = create_connection
    SFTP_with_mocked_get.get_file = get_file

    sftp = generate_live_sftp_connection()
    sup(sftp, simple_csv_path, simple_compressed_csv_path)

    yield sftp, get

    cleanup(sftp)


#
# Tests
#


def test_credential_validation():
    with pytest.raises(ValueError):
        SFTP(host=None, username=None, password=None)

    with pytest.raises(ValueError):
        SFTP(host=None, username="sam", password="abc123")


@mark_live_test
def test_list_non_existent_directory(live_sftp):
    with pytest.raises(FileNotFoundError):
        live_sftp.list_directory("abc123")


@mark_live_test
def test_list_directory_with_files(live_sftp):
    result = sorted(live_sftp.list_directory(REMOTE_DIR))
    assert result == [EMPTY, SUBDIR_A, SUBDIR_B, CSV, COMPRESSED_CSV]


@mark_live_test
def test_get_non_existent_file(live_sftp):
    with pytest.raises(FileNotFoundError):
        live_sftp.get_file("abc123")


# Helper function
def assert_file_matches_table(local_path, table):
    downloaded_tbl = Table.from_csv(local_path)
    assert_matching_tables(table, downloaded_tbl)


@mark_live_test
def test_get_file(live_sftp, simple_table):  # noqa F811
    local_path = file_util.create_temp_file()
    live_sftp.get_file(CSV_PATH, local_path=local_path)
    assert_file_matches_table(local_path, simple_table)


@mark_live_test
def test_get_table(live_sftp, simple_table):  # noqa F811
    file_util.create_temp_file()
    tbl = live_sftp.get_table(CSV_PATH)
    assert_matching_tables(tbl, simple_table)


@mark_live_test
def test_get_temp_file(live_sftp, simple_table):  # noqa F811
    local_path = live_sftp.get_file(CSV_PATH)
    assert_file_matches_table(local_path, simple_table)


@mark_live_test
@pytest.mark.parametrize("compression", [None, "gzip"])
def test_table_to_sftp_csv(live_sftp, simple_table, compression):  # noqa F811
    host = os.environ["SFTP_HOST"]
    username = os.environ["SFTP_USERNAME"]
    password = os.environ["SFTP_PASSWORD"]
    remote_path = f"{REMOTE_DIR}/test_to_sftp.csv"
    if compression == "gzip":
        remote_path += ".gz"
    simple_table.to_sftp_csv(remote_path, host, username, password, compression=compression)

    local_path = live_sftp.get_file(remote_path)
    assert_file_matches_table(local_path, simple_table)

    # Cleanup
    live_sftp.remove_file(remote_path)


#
# Helper Functions
#


def assert_results_match_expected(expected, results):
    assert len(results) == len(expected)
    for e in expected:
        assert any([e in r for r in results])


def assert_has_call(mock, args):
    return call(*args) in mock.mock_calls


def assert_has_calls(mock, calls):
    return all([assert_has_call(mock, c) for c in calls])


@mark_live_test
def test_list_files(live_sftp):
    result = sorted(live_sftp.list_files(REMOTE_DIR))
    assert result == [CSV_PATH, COMPRESSED_CSV_PATH]


@mark_live_test
def test_list_files_with_pattern(live_sftp):
    result = live_sftp.list_files(REMOTE_DIR, pattern="gz")
    assert result == [COMPRESSED_CSV_PATH]


@mark_live_test
def test_list_subdirectories(live_sftp):
    result = sorted(live_sftp.list_subdirectories(REMOTE_DIR))
    assert result == [EMPTY_PATH, SUBDIR_A_PATH, SUBDIR_B_PATH]


@mark_live_test
def test_list_subdirectories_with_pattern(live_sftp):
    result = sorted(live_sftp.list_subdirectories(REMOTE_DIR, pattern="sub"))
    assert result == [SUBDIR_A_PATH, SUBDIR_B_PATH]


local_paths = ["foo", "bar"]

# The following are values for the arguments to pass to `get_files` and `walk_tree` as well as the
# strings expected to be found in the returned results.
args_and_expected = {
    "get_files": [
        ({"remote": REMOTE_DIR}, [CSV_PATH, COMPRESSED_CSV_PATH]),
        ({"remote": [SUBDIR_A_PATH, SUBDIR_B_PATH]}, [CSV_B_PATH, CSV_A_PATH]),
        (
            {"remote": SUBDIR_B_PATH, "files_to_download": [CSV_B_PATH]},
            [CSV_A_PATH, CSV_B_PATH],
        ),
        ({"remote": [SUBDIR_A_PATH, SUBDIR_B_PATH], "pattern": "a"}, [CSV_B_PATH]),
    ],
    "walk_tree": [
        (
            [REMOTE_DIR],
            {"download": False, "dir_pattern": SUBDIR_A},
            [[SUBDIR_A], [COMPRESSED_CSV, CSV, CSV_B]],
        ),
        (
            [REMOTE_DIR],
            {"download": False, "file_pattern": CSV_B},
            [[SUBDIR_A, SUBDIR_B, EMPTY], [CSV_B]],
        ),
        (
            [REMOTE_DIR],
            {"download": False, "dir_pattern": SUBDIR_A, "file_pattern": CSV_B},
            [[SUBDIR_A], [CSV_B]],
        ),
        (
            [REMOTE_DIR],
            {"download": False, "max_depth": 1},
            [[EMPTY, SUBDIR_A, SUBDIR_B], [CSV, COMPRESSED_CSV]],
        ),
    ],
}


@mark_live_test
def test_get_files_calls_get_to_write_to_provided_local_paths(
    live_sftp_with_mocked_get,
):
    live_sftp, get = live_sftp_with_mocked_get
    results = live_sftp.get_files(remote=[SUBDIR_A_PATH, SUBDIR_B_PATH], local_paths=local_paths)
    assert get.call_count == 2
    calls = [call(CSV_A_PATH, local_paths[0]), call(CSV_B_PATH, local_paths[1])]
    assert_has_calls(get, calls)
    assert_results_match_expected(local_paths, results)


@mark_live_test
@pytest.mark.parametrize("kwargs,expected", args_and_expected["get_files"])
def test_get_files_calls_get_to_write_temp_files(kwargs, expected, live_sftp_with_mocked_get):
    live_sftp, get = live_sftp_with_mocked_get
    live_sftp.get_files(**kwargs)
    assert get.call_count == len(expected)
    calls = [call(e, local_paths[i]) for i, e in enumerate(expected)]
    assert_has_calls(get, calls)


@mark_live_test
def test_get_files_raises_error_when_no_file_source_is_provided(live_sftp):
    with pytest.raises(ValueError):
        live_sftp.get_files()


@mark_live_test
@patch("parsons.sftp.SFTP.get_file")
def test_get_files_with_files_paths_mismatch(get_file, live_sftp):
    live_sftp.get_files(files_to_download=[CSV_A_PATH], local_paths=local_paths)
    assert get_file.call_args[1]["local_path"] is None


@mark_live_test
@pytest.mark.parametrize("args,kwargs,expected", args_and_expected["walk_tree"])
def test_walk_tree(args, kwargs, expected, live_sftp_with_mocked_get):
    live_sftp, get = live_sftp_with_mocked_get
    results = live_sftp.walk_tree(*args, **kwargs)
    # `results` will be a list of first dirs then files, as will `expected`
    for res, expect in zip(results, expected):
        assert_results_match_expected(expect, res)


# Stuff that is tested by the live_sftp fixture, so no need to test explicitly:
# test_make_directory
# test_put_file
# test_put_file_compressed
# def test_remove_file
# def test_remove_directory
