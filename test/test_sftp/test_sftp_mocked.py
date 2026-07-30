"""SFTP operation tests that run in CI (no live server).

SFTP speaks a stateful protocol via paramiko, and every method accepts a
``connection`` argument, so we inject a ``FakeSFTP`` (see fakes.py) and assert the
connector translates each call into the right paramiko operation. The rest of the
suite (test_sftp.py, test_sftp_ssh.py) exercises the same paths against a real
server and is skipped by default.
"""

import pytest

from parsons import Table
from test.conftest import assert_matching_tables

from .fakes import FakeAttr, FakeSFTP


def calls_of(fake, name):
    return [c for c in fake.calls if c[0] == name]


def test_list_directory(sftp):
    fake = FakeSFTP(entries=[FakeAttr("a.csv"), FakeAttr("sub", is_dir=True)])

    result = sftp.list_directory("parsons_test", connection=fake)

    assert result == ["a.csv", "sub"]
    assert calls_of(fake, "listdir") == [("listdir", (), {"path": "parsons_test"})]


def test_make_directory(sftp):
    fake = FakeSFTP()

    sftp.make_directory("parsons_test/new", connection=fake)

    assert calls_of(fake, "mkdir") == [("mkdir", ("parsons_test/new",), {})]


def test_remove_directory(sftp):
    fake = FakeSFTP()

    sftp.remove_directory("parsons_test/old", connection=fake)

    assert calls_of(fake, "rmdir") == [("rmdir", ("parsons_test/old",), {})]


def test_remove_file(sftp):
    fake = FakeSFTP()

    sftp.remove_file("parsons_test/f.csv", connection=fake)

    assert calls_of(fake, "remove") == [("remove", ("parsons_test/f.csv",), {})]


def test_get_file_to_given_path(sftp):
    fake = FakeSFTP()

    result = sftp.get_file("parsons_test/f.csv", local_path="/tmp/out.csv", connection=fake)

    assert result == "/tmp/out.csv"
    assert calls_of(fake, "get") == [("get", ("parsons_test/f.csv", "/tmp/out.csv"), {})]


def test_get_file_defaults_to_temp_path(sftp):
    fake = FakeSFTP()

    result = sftp.get_file("parsons_test/f.csv", connection=fake)

    # With no local_path, a temp file is created and the download targets it.
    assert result
    assert calls_of(fake, "get") == [("get", ("parsons_test/f.csv", result), {})]


def test_put_file_passes_progress_callback(sftp):
    fake = FakeSFTP()

    sftp.put_file("/tmp/local.csv", "parsons_test/remote.csv", connection=fake)

    (put,) = calls_of(fake, "put")
    assert put[1] == ("/tmp/local.csv", "parsons_test/remote.csv")
    assert put[2]["callback"] == sftp._progress


def test_put_file_verbose_false_has_no_callback(sftp):
    fake = FakeSFTP()

    sftp.put_file("/tmp/local.csv", "parsons_test/remote.csv", connection=fake, verbose=False)

    (put,) = calls_of(fake, "put")
    assert put[2]["callback"] is None


def test_get_file_size(sftp):
    fake = FakeSFTP(size=2048)

    # get_file_size divides the byte size reported by the server by 1024.
    assert sftp.get_file_size("parsons_test/f.csv", connection=fake) == 2.0
    assert calls_of(fake, "file") == [("file", ("parsons_test/f.csv", "r"), {})]


def test_list_files(sftp):
    fake = FakeSFTP(entries=[FakeAttr("a.csv"), FakeAttr("b.txt"), FakeAttr("sub", is_dir=True)])

    assert sftp.list_files("parsons_test", connection=fake) == [
        "parsons_test/a.csv",
        "parsons_test/b.txt",
    ]


def test_list_files_with_pattern(sftp):
    fake = FakeSFTP(entries=[FakeAttr("a.csv"), FakeAttr("b.txt")])

    assert sftp.list_files("parsons_test", connection=fake, pattern="csv") == ["parsons_test/a.csv"]


def test_list_subdirectories(sftp):
    fake = FakeSFTP(
        entries=[FakeAttr("a.csv"), FakeAttr("sub_a", is_dir=True), FakeAttr("sub_b", is_dir=True)]
    )

    assert sftp.list_subdirectories("parsons_test", connection=fake) == [
        "parsons_test/sub_a",
        "parsons_test/sub_b",
    ]


def test_list_files_empty_directory(sftp):
    # paramiko raises FileNotFoundError when listing an empty directory; it is swallowed.
    fake = FakeSFTP(listdir_attr_error=FileNotFoundError())

    assert sftp.list_files("parsons_test/empty", connection=fake) == []
    assert sftp.list_subdirectories("parsons_test/empty", connection=fake) == []


def test_get_table(sftp, shared_datadir, simple_table):
    fake = FakeSFTP(get_source=str(shared_datadir / "test-simple-table.csv"))

    tbl = sftp.get_table("parsons_test/test.csv", connection=fake)

    assert_matching_tables(tbl, simple_table)


def test_get_table_rejects_non_table_suffix(sftp):
    fake = FakeSFTP()

    with pytest.raises(ValueError, match="cannot be converted to a Parsons table"):
        sftp.get_table("parsons_test/notes.pdf", connection=fake)


def test_get_files_from_remote_dir(sftp):
    fake = FakeSFTP(entries=[FakeAttr("a.csv"), FakeAttr("b.csv")])

    results = sftp.get_files(remote="parsons_test", connection=fake)

    assert len(results) == 2
    downloaded = [get[1][0] for get in calls_of(fake, "get")]
    assert downloaded == ["parsons_test/a.csv", "parsons_test/b.csv"]


def test_get_files_to_explicit_local_paths(sftp):
    fake = FakeSFTP()

    results = sftp.get_files(
        files_to_download=["parsons_test/a.csv"], local_paths=["/tmp/a.csv"], connection=fake
    )

    assert results == ["/tmp/a.csv"]
    assert calls_of(fake, "get") == [("get", ("parsons_test/a.csv", "/tmp/a.csv"), {})]


def test_get_files_requires_a_source(sftp):
    fake = FakeSFTP()

    with pytest.raises(ValueError, match="must provide either"):
        sftp.get_files(connection=fake)


def test_get_table_returns_parsons_table(sftp, shared_datadir):
    fake = FakeSFTP(get_source=str(shared_datadir / "test-simple-table.csv"))

    assert isinstance(sftp.get_table("parsons_test/test.csv", connection=fake), Table)
