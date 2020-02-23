from parsons import Postgres, DBSync, Table, Redshift
from test.utils import assert_matching_tables
import unittest
import os

_dir = os.path.dirname(__file__)

TEMP_SCHEMA = 'parsons_test'


# These tests interact directly with the Postgres database. In order to run, set the
# env to LIVE_TEST='TRUE'.
@unittest.skipIf(not os.environ.get('LIVE_TEST'), 'Skipping because not running live test')
class TestPostgresDBSync(unittest.TestCase):

    def setUp(self):

        self.temp_schema = TEMP_SCHEMA
        self.db = Postgres()

        # Create a schema.
        setup_sql = f"""
                     DROP SCHEMA IF EXISTS {self.temp_schema} CASCADE;
                     CREATE SCHEMA {self.temp_schema};
                     """
        self.db.query(setup_sql)

        # Load dummy data to parsons tables
        self.table1 = Table.from_csv(f'{_dir}/test_data/sample_table_1.csv')
        self.table2 = Table.from_csv(f'{_dir}/test_data/sample_table_2.csv')

        # Create source table
        self.db.copy(self.table1, f'{self.temp_schema}.source')

        # Create DB Sync object
        self.db_sync = DBSync(self.db, self.db)

    def tearDown(self):
        # Drop the view, the table and the schema

        teardown_sql = f"""
                       DROP SCHEMA IF EXISTS {self.temp_schema} CASCADE;
                       """
        self.db.query(teardown_sql)

    def test_table_sync_full_drop(self):
        # Test a db sync with drop.

        self.db_sync.table_sync_full(f'{self.temp_schema}.source',
                                     f'{self.temp_schema}.destination')

        source = self.db.query(f"SELECT * FROM {self.temp_schema}.source")
        destination = self.db.query(f"SELECT * FROM {self.temp_schema}.destination")
        assert_matching_tables(source, destination)

    def test_table_sync_full_truncate(self):
        # Test a db sync with truncate.

        self.db_sync.table_sync_full(f'{self.temp_schema}.source',
                                      f'{self.temp_schema}.destination',
                                     if_exists='truncate')
        source = self.db.query(f"SELECT * FROM {self.temp_schema}.source")
        destination = self.db.query(f"SELECT * FROM {self.temp_schema}.destination")
        assert_matching_tables(source, destination)

    def test_table_sync_full_empty_table(self):
        # Test a full sync of a table when the source table is empty.

        # Empty the source table
        self.db.query(f"TRUNCATE {self.temp_schema}.source")

        # Attempt to sync.
        self.db_sync.table_sync_full(f'{self.temp_schema}.source',
                                      f'{self.temp_schema}.destination')


    def test_table_sync_full_chunk(self):
        # Test chunking in full sync.

        self.db_sync.chunk_size = 10
        self.db_sync.table_sync_full(f'{self.temp_schema}.source',
                                     f'{self.temp_schema}.destination')

        source = self.db.query(f"SELECT * FROM {self.temp_schema}.source")
        destination = self.db.query(f"SELECT * FROM {self.temp_schema}.destination")
        assert_matching_tables(source, destination)

    def test_table_sync_incremental(self):
        # Test that incremental sync

        self.db.copy(self.table1, f'{self.temp_schema}.destination')
        self.db.copy(self.table2, f'{self.temp_schema}.source', if_exists='append')
        self.db_sync.table_sync_incremental(f'{self.temp_schema}.source',
                                            f'{self.temp_schema}.destination',
                                            'pk')

        count1 = self.db.query(f"SELECT * FROM {self.temp_schema}.source")
        count2 = self.db.query(f"SELECT * FROM {self.temp_schema}.destination")
        assert_matching_tables(count1, count2)

    def test_table_sync_incremental_chunk(self):
        # Test chunking of incremental sync.

        self.db_sync.chunk_size = 10
        self.db.copy(self.table1, f'{self.temp_schema}.destination')
        self.db.copy(self.table2, f'{self.temp_schema}.source', if_exists='append')
        self.db_sync.table_sync_incremental(f'{self.temp_schema}.source',
                                            f'{self.temp_schema}.destination',
                                            'pk')

        count1 = self.db.query(f"SELECT * FROM {self.temp_schema}.source")
        count2 = self.db.query(f"SELECT * FROM {self.temp_schema}.destination")
        assert_matching_tables(count1, count2)

    def test_table_sync_incremental_create_destination_table(self):
        # Test that an incremental sync works if the destination table does not exist.

        self.db_sync.table_sync_incremental(f'{self.temp_schema}.source',
                                            f'{self.temp_schema}.destination',
                                            'pk')

        count1 = self.db.query(f"SELECT * FROM {self.temp_schema}.source")
        count2 = self.db.query(f"SELECT * FROM {self.temp_schema}.destination")
        assert_matching_tables(count1, count2)

    def test_table_sync_incremental_empty_table(self):
        # Test an incremental sync of a table when the source table is empty.

        # Empty the source table
        self.db.query(f"TRUNCATE {self.temp_schema}.source")

        # Attempt to sync.
        self.db_sync.table_sync_incremental(f'{self.temp_schema}.source',
                                            f'{self.temp_schema}.destination',
                                            'pk')

# These tests interact directly with the Postgres database. In order to run, set the
# env to LIVE_TEST='TRUE'.
@unittest.skipIf(not os.environ.get('LIVE_TEST'), 'Skipping because not running live test')
class TestRedshiftDBSync(TestPostgresDBSync):
    """ This test inherits all of the tests from the Postgres test. """

    def setUp(self):

        self.temp_schema = TEMP_SCHEMA
        self.db = Redshift()

        # Create a schema.
        setup_sql = f"""
                     DROP SCHEMA IF EXISTS {self.temp_schema} CASCADE;
                     CREATE SCHEMA {self.temp_schema};
                     """
        self.db.query(setup_sql)

        # Load dummy data to parsons tables
        self.table1 = Table.from_csv(f'{_dir}/test_data/sample_table_1.csv')
        self.table2 = Table.from_csv(f'{_dir}/test_data/sample_table_2.csv')

        # Create source table
        self.db.copy(self.table1, f'{self.temp_schema}.source')

        # Create DB Sync object
        self.db_sync = DBSync(self.db, self.db)
