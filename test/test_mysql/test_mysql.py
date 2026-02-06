import unittest

from parsons import MySQL, Table
from parsons.databases.mysql.create_table import MySQLCreateTable
from test.conftest import assert_matching_tables, mark_live_test


# These tests interact directly with the MySQL database. To run, set env variable "LIVE_TEST=True"
@mark_live_test
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
        assert r.first == 1

    def test_query_no_response(self):
        # Check that a query that has no response and doesn't fail
        sql = "CREATE TABLE test (name VARCHAR(255), user_name VARCHAR(255))"
        r = self.mysql.query(sql)
        assert r is None

    def test_insert_data(self):
        sql = "CREATE TABLE test (name VARCHAR(255), user_name VARCHAR(255));"
        self.mysql.query(sql)

        sql = "INSERT INTO test (name, user_name) VALUES ('me', 'myuser');"
        self.mysql.query(sql)

        r = self.mysql.query("select * from test")

        assert_matching_tables(Table([{"name": "me", "user_name": "myuser"}]), r)


# These tests interact directly with the MySQL database. To run, set env variable "LIVE_TEST=True"
@mark_live_test
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
        assert self.tbl.num_rows == 3

    def test_max_primary_key(self):
        assert self.tbl.max_primary_key("id") == 3

    def test_distinct_primary_key(self):
        assert self.tbl.distinct_primary_key("id")
        assert not self.tbl.distinct_primary_key("user_name")

    def test_columns(self):
        assert self.tbl.columns == ["name", "user_name", "id"]

    def test_exists(self):
        assert self.tbl.exists

        tbl_bad = MySQLCreateTable(self.mysql, "bad_test")
        assert not tbl_bad.exists

    def test_drop(self):
        self.tbl.drop()
        assert not self.tbl.exists

    def test_truncate(self):
        self.tbl.truncate()
        assert self.tbl.num_rows == 0

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
        assert self.tbl.get_new_rows_count("id", 1) == 2


# TODO: figure out why there are 2 of these
class TestMySQL(unittest.TestCase):  # noqa: F811
    def setUp(self):
        self.mysql = MySQL(username="test", password="test", host="test", db="test", port=123)

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
        assert self.mysql.data_type(False, "") == "bool"
        assert self.mysql.data_type(True, "") == "bool"

        # Test smallint
        assert self.mysql.data_type(1, "") == "smallint"
        assert self.mysql.data_type(2, "") == "smallint"
        # Test int
        assert self.mysql.data_type(32769, "") == "mediumint"
        # Test bigint
        assert self.mysql.data_type(2147483648, "") == "bigint"
        # Test varchar that looks like an int
        assert self.mysql.data_type("00001", "") == "varchar"
        # Test a float as a decimal
        assert self.mysql.data_type(5.001, "") == "float"
        # Test varchar
        assert self.mysql.data_type("word", "") == "varchar"
        # Test int with underscore as string
        assert self.mysql.data_type("1_2", "") == "varchar"
        # Test int with underscore
        assert self.mysql.data_type(12, "") == "smallint"
        # Test int with leading zero
        assert self.mysql.data_type("01", "") == "varchar"

    def test_evaluate_table(self):
        table_map = [
            {"name": "ID", "type": "smallint", "width": 0},
            {"name": "Name", "type": "varchar", "width": 8},
            {"name": "Score", "type": "float", "width": 0},
        ]
        assert self.mysql.evaluate_table(self.tbl) == table_map

    def test_create_statement(self):
        stmt = "CREATE TABLE test_table ( \n id smallint \n,name varchar(10) \n,score float \n);"
        assert self.mysql.create_statement(self.tbl, "test_table") == stmt
