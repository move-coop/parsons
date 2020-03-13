from parsons.databases.mysql.mysql import MySQL
from parsons.etl.table import Table
from test.utils import assert_matching_tables
import unittest
import os

# The name of the schema and will be temporarily created for the tests
TEMP_SCHEMA = 'parsons_test'


# These tests interact directly with the Postgres database. To run, set env variable "LIVE_TEST=True"
@unittest.skipIf(not os.environ.get('LIVE_TEST'), 'Skipping because not running live test')
class TestMySQL(unittest.TestCase):

    def setUp(self):

        self.temp_schema = TEMP_SCHEMA
        self.mysql = MySQL()

    def tearDown(self):

        # Drop the view, the table and the schema
        sql = f"DROP TABLE IF EXISTS test;"
        self.mysql.query(sql)

    def test_query(self):

        # Check that query sending back expected result
        r = self.mysql.query("SELECT 1")
        self.assertEqual(r.first, 1)

    def test_query_no_response(self):

        # Check that a query that has no response and doesn't fail
        sql = f"CREATE TABLE test (name VARCHAR(255), user_name VARCHAR(255))"
        r = self.mysql.query(sql)
        self.assertEqual(r, None)

    def test_insert_data(self):

        sql = "CREATE TABLE test (name VARCHAR(255), user_name VARCHAR(255));"
        self.mysql.query(sql)

        sql = "INSERT INTO test (name, user_name) VALUES ('me', 'myuser');"
        self.mysql.query(sql)

        r = self.mysql.query("select * from test")

        assert_matching_tables(Table([{'name': 'me', 'user_name': 'myuser'}]), r)