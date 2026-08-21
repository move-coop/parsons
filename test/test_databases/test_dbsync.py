"""Tests for DBSync across database backends.

The pre-migration suite parametrized these by subclassing an abstract ``TestCase``
once per backend (FakeDatabase, Sqlite, and live Postgres/Redshift). Here the same
matrix is expressed with a parametrized ``harness`` fixture: the FakeDatabase and
Sqlite backends run in CI, Postgres and Redshift are marked ``live`` and skipped by
default. Backend-specific tests take the ``fake_harness`` fixture instead.
"""

import tempfile
from pathlib import Path

import pytest

from parsons import DBSync, Postgres, Redshift, Table
from parsons.databases.sqlite import Sqlite
from test.conftest import assert_matching_tables
from test.test_databases.fakes import FakeDatabase

_dir = Path(__file__).parent
TEMP_SCHEMA = "parsons_test"


class DBSyncHarness:
    """A primed source + destination database for one DBSync backend."""

    def __init__(self, source_db, destination_db, temp_schema, setup_sql=None, teardown_sql=None):
        self.source_db = source_db
        self.destination_db = destination_db
        self.temp_schema = temp_schema
        self.teardown_sql = teardown_sql

        if setup_sql:
            self.source_db.query(setup_sql)
            self.destination_db.query(setup_sql)

        self.table1 = Table.from_csv(str(_dir / "test_data/sample_table_1.csv"))
        self.table2 = Table.from_csv(str(_dir / "test_data/sample_table_2.csv"))
        self.source_table = f"{temp_schema}.source_table" if temp_schema else "source_table"
        self.destination_table = (
            f"{temp_schema}.destination_table" if temp_schema else "destination_table"
        )

        self.source_db.copy(self.table1, self.source_table, if_exists="truncate")
        self.set_up_db_sync()

    def set_up_db_sync(self, **kwargs):
        self.db_sync = DBSync(self.source_db, self.destination_db, **kwargs)

    def table_sync_full(self, if_exists, **kwargs):
        self.db_sync.table_sync_full(
            self.source_table, self.destination_table, if_exists=if_exists, **kwargs
        )

    def assert_synced(self):
        source = self.source_db.query(f"SELECT * FROM {self.source_table}")
        destination = self.destination_db.query(f"SELECT * FROM {self.destination_table}")
        assert_matching_tables(source, destination)

    def teardown(self):
        if self.teardown_sql:
            self.source_db.query(self.teardown_sql)
            self.destination_db.query(self.teardown_sql)


def _make_harness(backend):
    if backend == "fake":
        return DBSyncHarness(FakeDatabase(), FakeDatabase(), temp_schema=TEMP_SCHEMA)
    if backend == "sqlite":
        return DBSyncHarness(
            Sqlite(tempfile.mkstemp()[1]), Sqlite(tempfile.mkstemp()[1]), temp_schema=None
        )
    # Live Postgres/Redshift: create and drop a scratch schema around the test.
    db = Postgres if backend == "postgres" else Redshift
    return DBSyncHarness(
        db(),
        db(),
        temp_schema=TEMP_SCHEMA,
        setup_sql=f"DROP SCHEMA IF EXISTS {TEMP_SCHEMA} CASCADE;\nCREATE SCHEMA {TEMP_SCHEMA};",
        teardown_sql=f"DROP SCHEMA IF EXISTS {TEMP_SCHEMA} CASCADE;",
    )


@pytest.fixture(
    params=[
        pytest.param("fake"),
        pytest.param("sqlite"),
        pytest.param("postgres", marks=pytest.mark.live),
        pytest.param("redshift", marks=pytest.mark.live),
    ]
)
def harness(request):
    built = _make_harness(request.param)
    yield built
    built.teardown()


@pytest.fixture
def fake_harness():
    return _make_harness("fake")


def test_table_sync_full_drop(harness):
    harness.table_sync_full(if_exists="drop")
    harness.assert_synced()


def test_table_sync_full_order_by(harness):
    harness.table_sync_full(if_exists="drop", order_by="data")
    rows = harness.destination_db.table(harness.destination_table).get_rows()

    # Rows were inserted in the expected order.
    assert rows[0]["pk"] == "010"
    assert rows[1]["pk"] == "012"
    assert rows[2]["pk"] == "028"


def test_table_sync_full_truncate(harness):
    harness.table_sync_full(if_exists="truncate")
    harness.assert_synced()


def test_table_sync_full_empty_table(harness):
    harness.source_db.table(harness.source_table).truncate()

    harness.table_sync_full(if_exists="drop", verify_row_count=False)


def test_table_sync_full_chunk(harness):
    harness.db_sync.chunk_size = 10
    harness.db_sync.table_sync_full(
        harness.source_table, harness.destination_table, if_exists="drop"
    )
    harness.assert_synced()


def test_table_sync_incremental(harness):
    harness.destination_db.copy(harness.table1, harness.destination_table)
    harness.source_db.copy(harness.table2, harness.source_table, if_exists="append")
    harness.db_sync.table_sync_incremental(harness.source_table, harness.destination_table, "pk")
    harness.assert_synced()


def test_table_sync_incremental_chunk(harness):
    harness.db_sync.chunk_size = 10
    harness.destination_db.copy(harness.table1, harness.destination_table)
    harness.source_db.copy(harness.table2, harness.source_table, if_exists="append")
    harness.db_sync.table_sync_incremental(harness.source_table, harness.destination_table, "pk")
    harness.assert_synced()


def test_table_sync_incremental_create_destination_table(harness):
    harness.db_sync.table_sync_incremental(harness.source_table, harness.destination_table, "pk")
    harness.assert_synced()


def test_table_sync_incremental_empty_table(harness):
    harness.source_db.table(harness.source_table).truncate()

    harness.db_sync.table_sync_incremental(
        harness.source_table, harness.destination_table, "pk", verify_row_count=False
    )


def test_table_sync_full_with_retry(fake_harness):
    # The destination copy fails twice, then succeeds on the third try.
    fake_harness.destination_db.setup_table("destination", Table(), failures=2)
    fake_harness.set_up_db_sync(retries=2)
    fake_harness.table_sync_full(if_exists="drop")
    fake_harness.assert_synced()


def test_table_sync_full_without_retry(fake_harness):
    # One failure with no retries surfaces as an error.
    fake_harness.destination_db.setup_table(fake_harness.destination_table, Table(), failures=1)
    with pytest.raises(ValueError, match="Canned error"):
        fake_harness.table_sync_full(if_exists="drop")


def test_table_sync_full_read_chunk(fake_harness):
    fake_harness.table_sync_full(if_exists="drop")
    fake_harness.assert_synced()

    # With default chunk sizes the whole table is written in a single copy. (The old
    # suite asserted len(copy_call_args[0]) == 3 — that the first call record had three
    # keys — a no-op that never checked the copy count at all.)
    assert len(fake_harness.destination_db.copy_call_args) == 1


def test_table_sync_full_write_chunk(fake_harness):
    fake_harness.set_up_db_sync(read_chunk_size=1, write_chunk_size=3)
    fake_harness.table_sync_full(if_exists="drop")
    fake_harness.assert_synced()

    # A small write chunk size splits the write into multiple copy calls.
    assert len(fake_harness.destination_db.copy_call_args) > 1
