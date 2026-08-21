import tempfile

import pytest

from parsons import Table
from parsons.databases.sqlite import Sqlite
from test.conftest import assert_matching_tables


@pytest.fixture
def sqlite():
    return Sqlite(tempfile.mkstemp(suffix=".db")[1])


@pytest.fixture
def people_table():
    return Table([["ID", "Name"], [1, "Jim"], [2, "John"], [3, "Sarah"]])


def _count(sqlite, table):
    return sqlite.query(f"select count(*) as count from {table}")[0]["count"]


def test_copy(sqlite, people_table):
    sqlite.copy(people_table, "tbl1", if_exists="drop")

    assert_matching_tables(people_table, sqlite.query("select * from tbl1"))


def test_copy_no_cli(sqlite, people_table):
    sqlite.copy(people_table, "tbl1", if_exists="drop", force_python_sdk=True)

    assert_matching_tables(people_table, sqlite.query("select * from tbl1"))


def test_copy_append(sqlite, people_table):
    sqlite.copy(people_table, "tbl1", if_exists="drop")
    sqlite.copy(people_table, "tbl1", if_exists="append")

    assert _count(sqlite, "tbl1") == 6


def test_copy_fail(sqlite, people_table):
    sqlite.copy(people_table, "tbl1", if_exists="drop")

    with pytest.raises(ValueError):  # noqa: PT011 - the connector raises a plain ValueError
        sqlite.copy(people_table, "tbl1", if_exists="fail")


def test_copy_truncate(sqlite, people_table):
    sqlite.copy(people_table, "tbl1", if_exists="drop")
    sqlite.copy(people_table, "tbl1", if_exists="truncate")

    assert _count(sqlite, "tbl1") == 3
