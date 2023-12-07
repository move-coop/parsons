from parsons import MySQL, Table
from parsons.databases.mysql.create_table import MySQLCreateTable
from test.utils import assert_matching_tables
import unittest
import os


# These tests interact directly with the MySQL database. To run, set env variable "LIVE_TEST=True"
@unittest.skipIf(
    not os.environ.get("LIVE_TEST"), "Skipping because not running live test"
)
class TestMySQLLive(unittest.TestCase):
    def setUp(self):

        self.mysql = MySQL()

    def tearDown(self):

        # Drop the view, the table and the schema
        sql = "DROP TABLE IF EXISTS test;"
        self.mysql.query(sql)

    def test_query(self):

        # Check that query sending back expected result
        r = self.mysql.query("SELECT 1")
        self.assertEqual(r.first, 1)

    def test_query_no_response(self):

        # Check that a query that has no response and doesn't fail
        sql = "CREATE TABLE test (name VARCHAR(255), user_name VARCHAR(255))"
        r = self.mysql.query(sql)
        self.assertEqual(r, None)

    def test_insert_data(self):

        sql = "CREATE TABLE test (name VARCHAR(255), user_name VARCHAR(255));"
        self.mysql.query(sql)

        sql = "INSERT INTO test (name, user_name) VALUES ('me', 'myuser');"
        self.mysql.query(sql)

        r = self.mysql.query("select * from test")

        assert_matching_tables(Table([{"name": "me", "user_name": "myuser"}]), r)


# These tests interact directly with the MySQL database. To run, set env variable "LIVE_TEST=True"
@unittest.skipIf(
    not os.environ.get("LIVE_TEST"), "Skipping because not running live test"
)
class TestMySQL(unittest.TestCase):
    def setUp(self):

        self.mysql = MySQL()

        # Create tables
        self.mysql.query(
            "CREATE TABLE IF NOT EXISTS test (name VARCHAR(255), user_name VARCHAR(255), id INT)"
        )
        self.mysql.query(
            """
                         INSERT INTO test (name, user_name, id)
                         VALUES ('me', 'myuser', '1'),
                                ('you', 'hey', '2'),
                                ('you', 'hey', '3')
                         """
        )

        self.tbl = MySQLCreateTable(self.mysql, "test")

    def tearDown(self):

        self.mysql.query("DROP TABLE IF EXISTS test;")

    def test_num_rows(self):

        self.assertEqual(self.tbl.num_rows, 3)

    def test_max_primary_key(self):

        self.assertEqual(self.tbl.max_primary_key("id"), 3)

    def test_distinct_primary_key(self):

        self.assertTrue(self.tbl.distinct_primary_key("id"))
        self.assertFalse(self.tbl.distinct_primary_key("user_name"))

    def test_columns(self):

        self.assertEqual(self.tbl.columns, ["name", "user_name", "id"])

    def test_exists(self):

        self.assertTrue(self.tbl.exists)

        tbl_bad = MySQLCreateTable(self.mysql, "bad_test")
        self.assertFalse(tbl_bad.exists)

    def test_drop(self):

        self.tbl.drop()
        self.assertFalse(self.tbl.exists)

    def test_truncate(self):

        self.tbl.truncate()
        self.assertEqual(self.tbl.num_rows, 0)

    def test_get_rows(self):

        data = [
            ["name", "user_name", "id"],
            ["me", "myuser", "1"],
            ["you", "hey", "2"],
            ["you", "hey", "3"],
        ]
        tbl = Table(data)

        assert_matching_tables(self.tbl.get_rows(), tbl)

    def test_get_new_rows(self):

        data = [["name", "user_name", "id"], ["you", "hey", "2"], ["you", "hey", "3"]]
        tbl = Table(data)

        # Basic
        assert_matching_tables(self.tbl.get_new_rows("id", 1), tbl)

        # Chunking
        assert_matching_tables(self.tbl.get_new_rows("id", 1, chunk_size=1), tbl)

    def test_get_new_rows_count(self):

        self.assertEqual(self.tbl.get_new_rows_count("id", 1), 2)


# TODO: figure out why there are 2 of these
class TestMySQL(unittest.TestCase):  # noqa
    def setUp(self):

        self.mysql = MySQL(
            username="test", password="test", host="test", db="test", port=123
        )

        self.tbl = Table(
            [
                ["ID", "Name", "Score"],
                [1, "Jim", 1.9],
                [2, "John", -0.5],
                [3, "Sarah", 0.0004],
            ]
        )

    def test_data_type(self):

        # Test bool
        self.assertEqual(self.mysql.data_type(False, ""), "bool")
        self.assertEqual(self.mysql.data_type(True, ""), "bool")

        # Test smallint
        self.assertEqual(self.mysql.data_type(1, ""), "smallint")
        self.assertEqual(self.mysql.data_type(2, ""), "smallint")
        # Test int
        self.assertEqual(self.mysql.data_type(32769, ""), "mediumint")
        # Test bigint
        self.assertEqual(self.mysql.data_type(2147483648, ""), "bigint")
        # Test varchar that looks like an int
        self.assertEqual(self.mysql.data_type("00001", ""), "varchar")
        # Test a float as a decimal
        self.assertEqual(self.mysql.data_type(5.001, ""), "float")
        # Test varchar
        self.assertEqual(self.mysql.data_type("word", ""), "varchar")
        # Test int with underscore as string
        self.assertEqual(self.mysql.data_type("1_2", ""), "varchar")
        # Test int with underscore
        self.assertEqual(self.mysql.data_type(1_2, ""), "smallint")
        # Test int with leading zero
        self.assertEqual(self.mysql.data_type("01", ""), "varchar")

    def test_evaluate_table(self):

        table_map = [
            {"name": "ID", "type": "smallint", "width": 0},
            {"name": "Name", "type": "varchar", "width": 8},
            {"name": "Score", "type": "float", "width": 0},
        ]
        self.assertEqual(self.mysql.evaluate_table(self.tbl), table_map)

    def test_create_statement(self):

        stmt = "CREATE TABLE test_table ( \n id smallint \n,name varchar(10) \n,score float \n);"
        self.assertEqual(self.mysql.create_statement(self.tbl, "test_table"), stmt)
