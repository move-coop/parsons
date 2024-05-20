from parsons import Postgres, Table
from test.utils import assert_matching_tables
import unittest
import os

# The name of the schema and will be temporarily created for the tests
TEMP_SCHEMA = "parsons_test"

# These tests do not interact with the Postgres Database directly, and don't need real credentials


class TestPostgresCreateStatement(unittest.TestCase):
    def setUp(self):

        self.pg = Postgres(username="test", password="test", host="test", db="test", port=123)

        self.tbl = Table([["ID", "Name"], [1, "Jim"], [2, "John"], [3, "Sarah"]])

        self.tbl2 = Table(
            [
                ["c1", "c2", "c3", "c4", "c5", "c6", "c7"],
                ["a", "", 1, "NA", 1.4, 1, 2],
                ["b", "", 2, "NA", 1.4, 1, 2],
                ["c", "", 3.4, "NA", "", "", "a"],
                ["d", "", 5, "NA", 1.4, 1, 2],
                ["e", "", 6, "NA", 1.4, 1, 2],
                ["f", "", 7.8, "NA", 1.4, 1, 2],
                ["g", "", 9, "NA", 1.4, 1, 2],
            ]
        )
        self.mapping = self.pg.generate_data_types(self.tbl)
        self.mapping2 = self.pg.generate_data_types(self.tbl2)

    def test_connection(self):

        # Test connection with kwargs passed
        Postgres(username="test", password="test", host="test", db="test")

        # Test connection with env variables
        os.environ["PGUSER"] = "user_env"
        os.environ["PGPASSWORD"] = "pass_env"
        os.environ["PGHOST"] = "host_env"
        os.environ["PGDATABASE"] = "db_env"
        os.environ["PGPORT"] = "5432"
        pg_env = Postgres()

        self.assertEqual(pg_env.username, "user_env")
        self.assertEqual(pg_env.password, "pass_env")
        self.assertEqual(pg_env.host, "host_env")
        self.assertEqual(pg_env.db, "db_env")
        self.assertEqual(pg_env.port, 5432)

    def test_data_type(self):
        # Test smallint
        self.assertEqual(self.pg.data_type(1, ""), "smallint")
        self.assertEqual(self.pg.data_type(2, ""), "smallint")
        # Test int
        self.assertEqual(self.pg.data_type(32769, ""), "int")
        # Test bigint
        self.assertEqual(self.pg.data_type(2147483648, ""), "bigint")
        # Test varchar that looks like an int
        self.assertEqual(self.pg.data_type("00001", ""), "varchar")
        # Test a float as a decimal
        self.assertEqual(self.pg.data_type(5.001, ""), "decimal")
        # Test varchar
        self.assertEqual(self.pg.data_type("word", ""), "varchar")
        # Test int with underscore as string
        self.assertEqual(self.pg.data_type("1_2", ""), "varchar")
        # Test int with leading zero as string
        self.assertEqual(self.pg.data_type("01", ""), "varchar")
        # Test int with underscore
        self.assertEqual(self.pg.data_type(1_2, ""), "smallint")

        # Test bool
        self.assertEqual(self.pg.data_type(True, ""), "bool")

    def test_generate_data_types(self):

        # Test correct header labels
        self.assertEqual(self.mapping["headers"], ["ID", "Name"])
        # Test correct data types
        self.assertEqual(self.mapping["type_list"], ["smallint", "varchar"])
        self.assertEqual(
            self.mapping2["type_list"],
            [
                "varchar",
                "varchar",
                "decimal",
                "varchar",
                "decimal",
                "smallint",
                "varchar",
            ],
        )
        # Test correct lengths
        self.assertEqual(self.mapping["longest"], [1, 5])

    def test_vc_padding(self):

        # Test padding calculated correctly
        self.assertEqual(self.pg.vc_padding(self.mapping, 0.2), [1, 6])

    def test_vc_max(self):

        # Test max sets it to the max
        self.assertEqual(self.pg.vc_max(self.mapping, ["Name"]), [1, 65535])

        # Test raises when can't find column
        # To Do

    def test_vc_validate(self):

        # Test that a column with a width of 0 is set to 1
        self.mapping["longest"][0] = 0
        self.mapping = self.pg.vc_validate(self.mapping)
        self.assertEqual(self.mapping, [1, 5])

    def test_create_sql(self):

        # Test the the statement is expected
        sql = self.pg.create_sql("tmc.test", self.mapping, distkey="ID")
        exp_sql = "create table tmc.test (\n  id smallint,\n  name varchar(5)) \ndistkey(ID) ;"
        self.assertEqual(sql, exp_sql)

    def test_column_validate(self):

        bad_cols = [
            "a",
            "a",
            "",
            "SELECT",
            "asdfjkasjdfklasjdfklajskdfljaskldfjaklsdfjlaksdfjklasjdfklasjdkfljaskldfljkasjdkfasjlkdfjklasdfjklakjsfasjkdfljaslkdfjklasdfjklasjkldfakljsdfjalsdkfjklasjdfklasjdfklasdkljf",  # noqa: E501
        ]
        fixed_cols = [
            "a",
            "a_1",
            "col_2",
            "col_3",
            "asdfjkasjdfklasjdfklajskdfljaskldfjaklsdfjlaksdfjklasjdfklasjdkfljaskldfljkasjdkfasjlkdfjklasdfjklakjsfasjkdfljaslkdfjkl",  # noqa: E501
        ]
        self.assertEqual(self.pg.column_name_validate(bad_cols), fixed_cols)

    def test_create_statement(self):

        # Assert that copy statement is expected
        sql = self.pg.create_statement(self.tbl, "tmc.test", distkey="ID")
        exp_sql = """create table tmc.test (\n  "id" smallint,\n  "name" varchar(5)) \ndistkey(ID) ;"""  # noqa: E501
        self.assertEqual(sql, exp_sql)

        # Assert that an error is raised by an empty table
        empty_table = Table([["Col_1", "Col_2"]])
        self.assertRaises(ValueError, self.pg.create_statement, empty_table, "tmc.test")


# These tests interact directly with the Postgres database


@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestPostgresDB(unittest.TestCase):
    def setUp(self):

        self.temp_schema = TEMP_SCHEMA
        self.pg = Postgres()

        self.tbl = Table([["ID", "Name"], [1, "Jim"], [2, "John"], [3, "Sarah"]])

        # Create a schema, create a table, create a view
        setup_sql = f"""
                    drop schema if exists {self.temp_schema} cascade;
                    create schema {self.temp_schema};
                    """

        other_sql = f"""
                    create table {self.temp_schema}.test (id smallint,name varchar(5));
                    create view {self.temp_schema}.test_view as (select * from {self.temp_schema}.test);
                    """  # noqa: E501

        self.pg.query(setup_sql)

        self.pg.query(other_sql)

    def tearDown(self):

        # Drop the view, the table and the schema
        teardown_sql = f"""
                       drop schema if exists {self.temp_schema} cascade;
                       """
        self.pg.query(teardown_sql)

    def test_query(self):

        # Check that query sending back expected result
        r = self.pg.query("select 1")
        self.assertEqual(r[0]["?column?"], 1)

    def test_query_with_parameters(self):
        table_name = f"{self.temp_schema}.test"
        self.pg.copy(self.tbl, f"{self.temp_schema}.test", if_exists="append")

        sql = f"select * from {table_name} where name = %s"
        name = "Sarah"
        r = self.pg.query(sql, parameters=[name])
        self.assertEqual(r[0]["name"], name)

        sql = f"select * from {table_name} where name in (%s, %s)"
        names = ["Sarah", "John"]
        r = self.pg.query(sql, parameters=names)
        self.assertEqual(r.num_rows, 2)

    def test_copy(self):

        # Copy a table and ensure table exists
        self.pg.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="drop")
        r = self.pg.query(f"select * from {self.temp_schema}.test_copy where name='Jim'")
        self.assertEqual(r[0]["id"], 1)

        # Copy table and ensure truncate works.
        self.pg.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="truncate")
        tbl = self.pg.query(f"select count(*) from {self.temp_schema}.test_copy")
        self.assertEqual(tbl.first, 3)

        # Copy table and ensure that drop works.
        self.pg.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="drop")
        tbl = self.pg.query(f"select count(*) from {self.temp_schema}.test_copy")
        self.assertEqual(tbl.first, 3)

        # Copy table and ensure that append works.
        self.pg.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="append")
        tbl = self.pg.query(f"select count(*) from {self.temp_schema}.test_copy")
        self.assertEqual(tbl.first, 6)

        # Try to copy the table and ensure that default fail works.
        self.assertRaises(ValueError, self.pg.copy, self.tbl, f"{self.temp_schema}.test_copy")

        # Try to copy the table and ensure that explicit fail works.
        self.assertRaises(
            ValueError,
            self.pg.copy,
            self.tbl,
            f"{self.temp_schema}.test_copy",
            if_exists="fail",
        )

    def test_to_postgres(self):

        self.tbl.to_postgres(f"{self.temp_schema}.test_copy")
        r = self.pg.query(f"select * from {self.temp_schema}.test_copy where name='Jim'")
        self.assertEqual(r[0]["id"], 1)

    def test_from_postgres(self):

        tbl = Table([["id", "name"], [1, "Jim"], [2, "John"], [3, "Sarah"]])

        self.pg.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="drop")
        out_tbl = self.tbl.from_postgres(f"SELECT * FROM {self.temp_schema}.test_copy")
        assert_matching_tables(out_tbl, tbl)


if __name__ == "__main__":
    unittest.main()
