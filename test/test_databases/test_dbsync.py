import os
import tempfile
import unittest
from abc import ABC
from typing import Optional, Type

from parsons import DBSync, Postgres, Redshift, Table
from parsons.databases.database_connector import DatabaseConnector
from parsons.databases.sqlite import Sqlite
from test.test_databases.fakes import FakeDatabase
from test.utils import assert_matching_tables

_dir = os.path.dirname(__file__)

TEMP_SCHEMA = "parsons_test"


class TestDBSync(ABC, unittest.TestCase):
    setup_sql: Optional[str] = None
    teardown_sql: Optional[str] = None
    temp_schema: Optional[str] = TEMP_SCHEMA
    db: Type[DatabaseConnector]

    @classmethod
    def setUpClass(cls):
        # Skip tests on this abstract base class
        if cls is TestDBSync:
            raise unittest.SkipTest("%s is an abstract base class" % cls.__name__)
        else:
            super(TestDBSync, cls).setUpClass()

    def setUp(self):
        self.initialize_db_connections()

        if self.setup_sql:
            self.source_db.query(self.setup_sql)
            self.destination_db.query(self.setup_sql)

        # Load dummy data to parsons tables
        self.table1 = Table.from_csv(f"{_dir}/test_data/sample_table_1.csv")
        self.table2 = Table.from_csv(f"{_dir}/test_data/sample_table_2.csv")

        self.source_table = (
            f"{self.temp_schema}.source_table" if self.temp_schema else "source_table"
        )
        self.destination_table = (
            f"{self.temp_schema}.destination_table" if self.temp_schema else "destination_table"
        )

        # Create source table
        self.source_db.copy(self.table1, self.source_table, if_exists="truncate")

        self.set_up_db_sync()

    def set_up_db_sync(self, **kwargs) -> None:
        # Create DB Sync object
        self.db_sync = DBSync(self.source_db, self.destination_db, **kwargs)

    def initialize_db_connections(self) -> None:
        self.source_db = self.db()
        self.destination_db = self.db()

    def tearDown(self):
        if self.teardown_sql:
            self.source_db.query(self.teardown_sql)
            self.destination_db.query(self.teardown_sql)

    def assert_matching_tables(self) -> None:
        source = self.source_db.query(f"SELECT * FROM {self.source_table}")
        destination = self.destination_db.query(f"SELECT * FROM {self.destination_table}")
        assert_matching_tables(source, destination)

    def table_sync_full(self, if_exists: str, **kwargs):
        self.db_sync.table_sync_full(
            self.source_table, self.destination_table, if_exists=if_exists, **kwargs
        )

    def test_table_sync_full_drop(self):
        self.table_sync_full(if_exists="drop")
        self.assert_matching_tables()

    def test_table_sync_full_order_by(self):
        self.table_sync_full(if_exists="drop", order_by="data")
        destination_table = self.destination_db.table(self.destination_table)
        rows = destination_table.get_rows()

        # Check that the rows were inserted in the expected order
        self.assertEqual(rows[0]["pk"], "010")
        self.assertEqual(rows[1]["pk"], "012")
        self.assertEqual(rows[2]["pk"], "028")

    def test_table_sync_full_truncate(self):
        self.table_sync_full(if_exists="truncate")
        self.assert_matching_tables()

    def test_table_sync_full_empty_table(self):
        # Empty the source table
        self.source_db.table(self.source_table).truncate()

        # Attempt to sync.
        self.table_sync_full(if_exists="drop", verify_row_count=False)

    def test_table_sync_full_chunk(self):
        # Test chunking in full sync.
        self.db_sync.chunk_size = 10
        self.db_sync.table_sync_full(self.source_table, self.destination_table, if_exists="drop")
        self.assert_matching_tables()

    def test_table_sync_incremental(self):
        # Test that incremental sync

        self.destination_db.copy(self.table1, self.destination_table)
        self.source_db.copy(self.table2, self.source_table, if_exists="append")
        self.db_sync.table_sync_incremental(self.source_table, self.destination_table, "pk")
        self.assert_matching_tables()

    def test_table_sync_incremental_chunk(self):
        # Test chunking of incremental sync.

        self.db_sync.chunk_size = 10
        self.destination_db.copy(self.table1, self.destination_table)
        self.source_db.copy(self.table2, self.source_table, if_exists="append")
        self.db_sync.table_sync_incremental(self.source_table, self.destination_table, "pk")

        self.assert_matching_tables()

    def test_table_sync_incremental_create_destination_table(self):
        # Test that an incremental sync works if the destination table does not exist.
        self.db_sync.table_sync_incremental(self.source_table, self.destination_table, "pk")
        self.assert_matching_tables()

    def test_table_sync_incremental_empty_table(self):
        # Test an incremental sync of a table when the source table is empty.

        # Empty the source table
        self.source_db.table(self.source_table).truncate()

        # Attempt to sync.
        self.db_sync.table_sync_incremental(
            self.source_table, self.destination_table, "pk", verify_row_count=False
        )


class TestFakeDBSync(TestDBSync):
    db = FakeDatabase

    def test_table_sync_full_with_retry(self):
        # Have the copy fail twice
        self.destination_db.setup_table("destination", Table(), failures=2)
        self.set_up_db_sync(retries=2)
        self.table_sync_full(if_exists="drop")
        self.assert_matching_tables()

    def test_table_sync_full_without_retry(self):
        # Have the copy fail
        self.destination_db.setup_table(self.destination_table, Table(), failures=1)
        # Make sure the sync results in an exception
        self.assertRaises(ValueError, lambda: self.table_sync_full(if_exists="drop"))

    def test_table_sync_full_read_chunk(self):
        self.table_sync_full(if_exists="drop")
        self.assert_matching_tables()

        # Make sure copy was called the expected number of times
        # read chunks of 2, 5 rows to write.. should be 3 copy calls
        self.assertEqual(
            len(self.destination_db.copy_call_args[0]),
            3,
            self.destination_db.copy_call_args[0],
        )

    def test_table_sync_full_write_chunk(self):
        self.set_up_db_sync(
            read_chunk_size=1,
            write_chunk_size=3,
        )
        self.table_sync_full(if_exists="drop")
        self.assert_matching_tables()

        # Make sure copy was called the expected number of times
        self.assertEqual(
            len(self.destination_db.copy_call_args[0]),
            3,
            self.destination_db.copy_call_args[0],
        )


class TestSqliteDBSync(TestDBSync):
    db = Sqlite
    temp_schema = None

    def initialize_db_connections(self) -> None:
        self.source_db = self.db(tempfile.mkstemp()[1])
        self.destination_db = self.db(tempfile.mkstemp()[1])


# These tests interact directly with the Postgres database. In order to run, set the
# env to LIVE_TEST='TRUE'.
@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestPostgresDBSync(TestDBSync):
    db = Postgres
    setup_sql = f"""
    DROP SCHEMA IF EXISTS {TEMP_SCHEMA} CASCADE;
    CREATE SCHEMA {TEMP_SCHEMA};
    """
    teardown_sql = f"""
    DROP SCHEMA IF EXISTS {TEMP_SCHEMA} CASCADE;
    """


# These tests interact directly with the Postgres database. In order to run, set the
# env to LIVE_TEST='TRUE'.
@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestRedshiftDBSync(TestPostgresDBSync):
    db = Redshift
