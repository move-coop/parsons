from parsons.databases.mysql.mysql import MySQL, MySQLTable
from parsons.etl.table import Table
from test.utils import assert_matching_tables
import unittest
import os


# These tests interact directly with the MySQL database. To run, set env variable "LIVE_TEST=True"
@unittest.skipIf(not os.environ.get('LIVE_TEST'), 'Skipping because not running live test')
class TestMySQL(unittest.TestCase):

    def setUp(self):

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


# These tests interact directly with the MySQL database. To run, set env variable "LIVE_TEST=True"
@unittest.skipIf(not os.environ.get('LIVE_TEST'), 'Skipping because not running live test')
class TestMySQL(unittest.TestCase):

    def setUp(self):

        self.mysql = MySQL()

        # Create tables
        self.mysql.query("CREATE TABLE IF NOT EXISTS test (name VARCHAR(255), user_name VARCHAR(255), id INT)")
        self.mysql.query("""
                         INSERT INTO test (name, user_name, id) 
                         VALUES ('me', 'myuser', '1'),
                                ('you', 'hey', '2'),
                                ('you', 'hey', '3')
                         """)

        self.tbl = MySQLTable(self.mysql, 'test')

    def tearDown(self):

        self.mysql.query("DROP TABLE IF EXISTS test;")

    def test_num_rows(self):

        self.assertEqual(self.tbl.num_rows, 3)

    def test_max_primary_key(self):

        self.assertEqual(self.tbl.max_primary_key('id'), 3)

    def test_distinct_primary_key(self):

        self.assertTrue(self.tbl.distinct_primary_key('id'))
        self.assertFalse(self.tbl.distinct_primary_key('user_name'))

    def test_columns(self):

        self.assertEqual(self.tbl.columns, ['name', 'user_name', 'id'])

    def test_exists(self):

        self.assertTrue(self.tbl.exists)

        tbl_bad = MySQLTable(self.mysql, 'bad_test')
        self.assertFalse(tbl_bad.exists)

    def test_drop(self):

        self.tbl.drop()
        self.assertFalse(self.tbl.exists)

    def test_truncate(self):

        self.tbl.truncate()
        self.assertEqual(self.tbl.num_rows, 0)

    def test_get_rows(self):

        pass

    def test_get_new_rows(self):

        pass