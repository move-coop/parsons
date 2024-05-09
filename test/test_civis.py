import unittest
import os
from parsons import CivisClient, Table

# from . import scratch_creds


@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestCivisClient(unittest.TestCase):
    def setUp(self):

        self.civis = CivisClient()

        # Create a schema, create a table, create a view
        setup_sql = """
                    drop schema if exists test_parsons cascade;
                    create schema test_parsons;
                    """

        self.lst_dicts = [{"first": "Bob", "last": "Smith"}]
        self.tbl = Table(self.lst_dicts)

        self.civis.query(setup_sql)

    def tearDown(self):

        # Drop the view, the table and the schema
        teardown_sql = """
                       drop schema if exists test_parsons cascade;
                       """

        self.civis.query(teardown_sql)

    def test_table_import_query(self):

        # Test that a good table imports correctly
        self.civis.table_import(self.tbl, "test_parsons.test_table")

    def test_query(self):

        # Test that queries match
        self.civis.table_import(self.tbl, "test_parsons.test_table")
        tbl = self.civis.query("SELECT COUNT(*) FROM test_parsons.test_table")
        self.assertEqual(tbl[0]["count"], "1")

    def test_to_civis(self):

        # Test that the to_civis() method works too
        self.tbl.to_civis("test_parsons.test_table")
