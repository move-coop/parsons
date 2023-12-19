from parsons import Redshift, S3, Table
from test.utils import assert_matching_tables
import unittest
import os
import re
from test.utils import validate_list
from testfixtures import LogCapture

# The name of the schema and will be temporarily created for the tests
TEMP_SCHEMA = "parsons_test2"

# These tests do not interact with the Redshift Database directly, and don't need real credentials


class TestRedshift(unittest.TestCase):
    def setUp(self):

        self.rs = Redshift(
            username="test", password="test", host="test", db="test", port=123
        )

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

        self.mapping = self.rs.generate_data_types(self.tbl)
        self.mapping2 = self.rs.generate_data_types(self.tbl2)

    def test_split_full_table_name(self):
        schema, table = Redshift.split_full_table_name("some_schema.some_table")
        self.assertEqual(schema, "some_schema")
        self.assertEqual(table, "some_table")

        # When missing the schema
        schema, table = Redshift.split_full_table_name("some_table")
        self.assertEqual(schema, "public")
        self.assertEqual(table, "some_table")

        # When there are too many parts
        self.assertRaises(ValueError, Redshift.split_full_table_name, "a.b.c")

    def test_combine_schema_and_table_name(self):
        full_table_name = Redshift.combine_schema_and_table_name(
            "some_schema", "some_table"
        )
        self.assertEqual(full_table_name, "some_schema.some_table")

    def test_data_type(self):
        # Test bool
        self.assertEqual(self.rs.data_type(True, ""), "bool")
        self.assertEqual(self.rs.data_type(1, ""), "int")
        # Test smallint
        # Currently smallints are coded as ints
        self.assertEqual(self.rs.data_type(2, ""), "int")
        # Test int
        self.assertEqual(self.rs.data_type(32769, ""), "int")
        # Test bigint
        self.assertEqual(self.rs.data_type(2147483648, ""), "bigint")
        # Test varchar that looks like an int
        self.assertEqual(self.rs.data_type("00001", ""), "varchar")
        # Test a float as a float
        self.assertEqual(self.rs.data_type(5.001, ""), "float")
        # Test varchar
        self.assertEqual(self.rs.data_type("word", ""), "varchar")
        # Test int with underscore as varchar
        self.assertEqual(self.rs.data_type("1_2", ""), "varchar")
        # Test int with underscore
        self.assertEqual(self.rs.data_type(1_2, ""), "int")
        # Test int with leading zero
        self.assertEqual(self.rs.data_type("01", ""), "varchar")

    def test_generate_data_types(self):
        # Test correct header labels
        self.assertEqual(self.mapping["headers"], ["ID", "Name"])
        # Test correct data types
        self.assertEqual(self.mapping["type_list"], ["int", "varchar"])

        self.assertEqual(
            self.mapping2["type_list"],
            ["varchar", "varchar", "float", "varchar", "float", "int", "varchar"],
        )

        # Test correct lengths
        self.assertEqual(self.mapping["longest"], [1, 5])

    def test_vc_padding(self):

        # Test padding calculated correctly
        self.assertEqual(self.rs.vc_padding(self.mapping, 0.2), [1, 6])

    def test_vc_max(self):

        # Test max sets it to the max
        self.assertEqual(self.rs.vc_max(self.mapping, ["Name"]), [1, 65535])

        # Test raises when can't find column
        # To Do

    def test_vc_validate(self):

        # Test that a column with a width of 0 is set to 1
        self.mapping["longest"][0] = 0
        self.mapping = self.rs.vc_validate(self.mapping)
        self.assertEqual(self.mapping, [1, 5])

    def test_create_sql(self):

        # Test the the statement is expected
        sql = self.rs.create_sql("tmc.test", self.mapping, distkey="ID")
        exp_sql = (
            "create table tmc.test (\n  id int,\n  name varchar(5)) \ndistkey(ID) ;"
        )
        self.assertEqual(sql, exp_sql)

    def test_compound_sortkey(self):
        # check single sortkey formatting
        sql = self.rs.create_sql("tmc.test", self.mapping, sortkey="ID")
        exp_sql = (
            "create table tmc.test (\n  id int,\n  name varchar(5)) \nsortkey(ID);"
        )
        self.assertEqual(sql, exp_sql)

        # check compound sortkey formatting
        sql = self.rs.create_sql("tmc.test", self.mapping, sortkey=["ID1", "ID2"])
        exp_sql = "create table tmc.test (\n  id int,\n  name varchar(5))"
        exp_sql += " \ncompound sortkey(ID1, ID2);"
        self.assertEqual(sql, exp_sql)

    def test_column_validate(self):

        bad_cols = [
            "a",
            "a",
            "",
            "SELECT",
            "asdfjkasjdfklasjdfklajskdfljaskldfjaklsdfjlaksdfjklasj"
            "dfklasjdkfljaskldfljkasjdkfasjlkdfjklasdfjklakjsfasjkdfljaslkdfjklasdfjklasjkl"
            "dfakljsdfjalsdkfjklasjdfklasjdfklasdkljf",
        ]
        fixed_cols = [
            "a",
            "a_1",
            "col_2",
            "col_3",
            "asdfjkasjdfklasjdfklajskdfljaskldfjaklsdfjlaks"
            "dfjklasjdfklasjdkfljaskldfljkasjdkfasjlkdfjklasdfjklakjsfasjkdfljaslkdfjkl",
        ]
        self.assertEqual(self.rs.column_name_validate(bad_cols), fixed_cols)

    def test_create_statement(self):

        # Assert that copy statement is expected
        sql = self.rs.create_statement(self.tbl, "tmc.test", distkey="ID")
        exp_sql = """create table tmc.test (\n  "id" int,\n  "name" varchar(5)) \ndistkey(ID) ;"""  # noqa: E501
        self.assertEqual(sql, exp_sql)

        # Assert that an error is raised by an empty table
        empty_table = Table([["Col_1", "Col_2"]])
        self.assertRaises(ValueError, self.rs.create_statement, empty_table, "tmc.test")

    def test_get_creds_kwargs(self):

        # Test passing kwargs
        creds = self.rs.get_creds("kwarg_key", "kwarg_secret_key")
        expected = """credentials 'aws_access_key_id=kwarg_key;aws_secret_access_key=kwarg_secret_key'\n"""  # noqa: E501
        self.assertEqual(creds, expected)

        # Test grabbing from environmental variables
        prior_aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "")
        prior_aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
        os.environ["AWS_ACCESS_KEY_ID"] = "env_key"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "env_secret_key"
        creds = self.rs.get_creds(None, None)
        expected = """credentials 'aws_access_key_id=env_key;aws_secret_access_key=env_secret_key'\n"""  # noqa: E501
        self.assertEqual(creds, expected)

        # Reset env vars
        os.environ["AWS_ACCESS_KEY_ID"] = prior_aws_access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = prior_aws_secret_access_key

    def scrub_copy_tokens(self, s):

        s = re.sub("=.+;", "=*HIDDEN*;", s)
        s = re.sub("aws_secret_access_key=.+'", "aws_secret_access_key=*HIDDEN*'", s)
        return s

    def test_copy_statement_default(self):

        sql = self.rs.copy_statement(
            "test_schema.test",
            "buck",
            "file.csv",
            aws_access_key_id="abc123",
            aws_secret_access_key="abc123",
            bucket_region="us-east-2",
        )

        # Scrub the keys
        sql = re.sub(
            r"id=.+;", "*id=HIDDEN*;", re.sub(r"key=.+'", "key=*HIDDEN*'", sql)
        )

        expected_options = [
            "ignoreheader 1",
            "acceptanydate",
            "dateformat 'auto'",
            "timeformat 'auto'",
            "csv delimiter ','",
            "copy test_schema.test \nfrom 's3://buck/file.csv'",
            "'aws_access_key_*id=HIDDEN*;aws_secret_access_key=*HIDDEN*'",
            "region 'us-east-2'",
            "emptyasnull",
            "blanksasnull",
            "acceptinvchars",
        ]

        # Check that all of the expected options are there:
        [self.assertNotEqual(sql.find(o), -1, o) for o in expected_options]

    def test_copy_statement_statupdate(self):

        sql = self.rs.copy_statement(
            "test_schema.test",
            "buck",
            "file.csv",
            aws_access_key_id="abc123",
            aws_secret_access_key="abc123",
            statupdate=True,
        )

        # Scrub the keys
        sql = re.sub(
            r"id=.+;", "*id=HIDDEN*;", re.sub(r"key=.+'", "key=*HIDDEN*'", sql)
        )

        expected_options = [
            "statupdate on",
            "ignoreheader 1",
            "acceptanydate",
            "dateformat 'auto'",
            "timeformat 'auto'",
            "csv delimiter ','",
            "copy test_schema.test \nfrom 's3://buck/file.csv'",
            "'aws_access_key_*id=HIDDEN*;aws_secret_access_key=*HIDDEN*'",
            "emptyasnull",
            "blanksasnull",
            "acceptinvchars",
        ]

        # Check that all of the expected options are there:
        [self.assertNotEqual(sql.find(o), -1) for o in expected_options]

        sql2 = self.rs.copy_statement(
            "test_schema.test",
            "buck",
            "file.csv",
            aws_access_key_id="abc123",
            aws_secret_access_key="abc123",
            statupdate=False,
        )

        # Scrub the keys
        sql2 = re.sub(
            r"id=.+;", "*id=HIDDEN*;", re.sub(r"key=.+'", "key=*HIDDEN*'", sql2)
        )

        expected_options = [
            "statupdate off",
            "ignoreheader 1",
            "acceptanydate",
            "dateformat 'auto'",
            "timeformat 'auto'",
            "csv delimiter ','",
            "copy test_schema.test \nfrom 's3://buck/file.csv'",
            "'aws_access_key_*id=HIDDEN*;aws_secret_access_key=*HIDDEN*'",
            "emptyasnull",
            "blanksasnull",
            "acceptinvchars",
        ]

        # Check that all of the expected options are there:
        [self.assertNotEqual(sql2.find(o), -1) for o in expected_options]

    def test_copy_statement_compupdate(self):

        sql = self.rs.copy_statement(
            "test_schema.test",
            "buck",
            "file.csv",
            aws_access_key_id="abc123",
            aws_secret_access_key="abc123",
            compupdate=True,
        )

        # Scrub the keys
        sql = re.sub(
            r"id=.+;", "*id=HIDDEN*;", re.sub(r"key=.+'", "key=*HIDDEN*'", sql)
        )

        expected_options = [
            "compupdate on",
            "ignoreheader 1",
            "acceptanydate",
            "dateformat 'auto'",
            "timeformat 'auto'",
            "csv delimiter ','",
            "copy test_schema.test \nfrom 's3://buck/file.csv'",
            "'aws_access_key_*id=HIDDEN*;aws_secret_access_key=*HIDDEN*'",
            "emptyasnull",
            "blanksasnull",
            "acceptinvchars",
        ]

        # Check that all of the expected options are there:
        [self.assertNotEqual(sql.find(o), -1) for o in expected_options]

        sql2 = self.rs.copy_statement(
            "test_schema.test",
            "buck",
            "file.csv",
            aws_access_key_id="abc123",
            aws_secret_access_key="abc123",
            compupdate=False,
        )

        # Scrub the keys
        sql2 = re.sub(
            r"id=.+;", "*id=HIDDEN*;", re.sub(r"key=.+'", "key=*HIDDEN*'", sql2)
        )

        expected_options = [
            "compupdate off",
            "ignoreheader 1",
            "acceptanydate",
            "dateformat 'auto'",
            "timeformat 'auto'",
            "csv delimiter ','",
            "copy test_schema.test \nfrom 's3://buck/file.csv'",
            "'aws_access_key_*id=HIDDEN*;aws_secret_access_key=*HIDDEN*'",
            "emptyasnull",
            "blanksasnull",
            "acceptinvchars",
        ]

        # Check that all of the expected options are there:
        [self.assertNotEqual(sql2.find(o), -1) for o in expected_options]

    def test_copy_statement_columns(self):

        cols = ["a", "b", "c"]

        sql = self.rs.copy_statement(
            "test_schema.test",
            "buck",
            "file.csv",
            aws_access_key_id="abc123",
            aws_secret_access_key="abc123",
            specifycols=cols,
        )

        # Scrub the keys
        sql = re.sub(
            r"id=.+;", "*id=HIDDEN*;", re.sub(r"key=.+'", "key=*HIDDEN*'", sql)
        )

        expected_options = [
            "ignoreheader 1",
            "acceptanydate",
            "dateformat 'auto'",
            "timeformat 'auto'",
            "csv delimiter ','",
            "copy test_schema.test(a, b, c) \nfrom 's3://buck/file.csv'",
            "'aws_access_key_*id=HIDDEN*;aws_secret_access_key=*HIDDEN*'",
            "emptyasnull",
            "blanksasnull",
            "acceptinvchars",
        ]

        # Check that all of the expected options are there:
        [self.assertNotEqual(sql.find(o), -1) for o in expected_options]


# These tests interact directly with the Redshift database


@unittest.skipIf(
    not os.environ.get("LIVE_TEST"), "Skipping because not running live test"
)
class TestRedshiftDB(unittest.TestCase):
    def setUp(self):

        self.temp_schema = TEMP_SCHEMA

        self.rs = Redshift()

        self.tbl = Table([["ID", "Name"], [1, "Jim"], [2, "John"], [3, "Sarah"]])

        # Create a schema, create a table, create a view
        setup_sql = f"""
                    drop schema if exists {self.temp_schema} cascade;
                    create schema {self.temp_schema};
                    """

        other_sql = f"""
                    create table {self.temp_schema}.test (id int,name varchar(5));
                    create view {self.temp_schema}.test_view as (
                        select * from {self.temp_schema}.test
                    );
        """

        self.rs.query(setup_sql)

        self.rs.query(other_sql)

        self.s3 = S3()

        self.temp_s3_bucket = os.environ["S3_TEMP_BUCKET"]
        self.temp_s3_prefix = "test/"

    def tearDown(self):

        # Drop the view, the table and the schema
        teardown_sql = f"""
                       drop schema if exists {self.temp_schema} cascade;
                       """
        self.rs.query(teardown_sql)

        # Remove all test objects from S3
        for key in self.s3.list_keys(self.temp_s3_bucket, self.temp_s3_prefix):
            self.s3.remove_file(self.temp_s3_bucket, key)

    def test_query(self):

        # Check that query sending back expected result
        r = self.rs.query("select 1")
        self.assertEqual(r[0]["?column?"], 1)

    def test_query_with_parameters(self):
        table_name = f"{self.temp_schema}.test"
        self.tbl.to_redshift(table_name, if_exists="append")

        sql = f"select * from {table_name} where name = %s"
        name = "Sarah"
        r = self.rs.query(sql, parameters=[name])
        self.assertEqual(r[0]["name"], name)

        sql = f"select * from {table_name} where name in (%s, %s)"
        names = ["Sarah", "John"]
        r = self.rs.query(sql, parameters=names)
        self.assertEqual(r.num_rows, 2)

    def test_schema_exists(self):
        self.assertTrue(self.rs.schema_exists(self.temp_schema))
        self.assertFalse(self.rs.schema_exists("nonsense"))

    def test_table_exists(self):

        # Check if table_exists finds a table that exists
        self.assertTrue(self.rs.table_exists(f"{self.temp_schema}.test"))

        # Check if table_exists is case insensitive
        self.assertTrue(self.rs.table_exists(f"{self.temp_schema.upper()}.TEST"))

        # Check if table_exists doesn't find a table that doesn't exists
        self.assertFalse(self.rs.table_exists(f"{self.temp_schema}.test_fake"))

        # Check if table_exists finds a table that exists
        self.assertTrue(self.rs.table_exists(f"{self.temp_schema}.test_view"))

        # Check if table_exists doesn't find a view that doesn't exists
        self.assertFalse(self.rs.table_exists(f"{self.temp_schema}.test_view_fake"))

        # Check that the view kwarg works
        self.assertFalse(
            self.rs.table_exists(f"{self.temp_schema}.test_view", view=False)
        )

    def test_temp_s3_create(self):

        key = self.rs.temp_s3_copy(self.tbl)

        # Test that you can get the object
        self.s3.get_file(self.temp_s3_bucket, key)

        # Try to delete the object
        self.rs.temp_s3_delete(key)

    def test_copy_s3(self):

        # To Do
        pass

    def test_copy(self):

        # Copy a table
        self.rs.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="drop")

        # Test that file exists
        r = self.rs.query(
            f"select * from {self.temp_schema}.test_copy where name='Jim'"
        )
        self.assertEqual(r[0]["id"], 1)

        # Copy to the same table, to verify that the "truncate" flag works.
        self.rs.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="truncate")
        rows = self.rs.query(f"select count(*) from {self.temp_schema}.test_copy")
        self.assertEqual(rows[0]["count"], 3)

        # Copy to the same table, to verify that the "drop" flag works.
        self.rs.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="drop")

        # Verify that a warning message prints when a DIST/SORT key is omitted
        with LogCapture() as lc:
            self.rs.copy(
                self.tbl,
                f"{self.temp_schema}.test_copy",
                if_exists="drop",
                sortkey="Name",
            )
            desired_log = [
                log for log in lc.records if "optimize your queries" in log.msg
            ][0]
            self.assertTrue("DIST" in desired_log.msg)
            self.assertFalse("SORT" in desired_log.msg)

    def test_upsert(self):

        # Create a target table when no target table exists
        self.rs.upsert(self.tbl, f"{self.temp_schema}.test_copy", "ID")

        # Run upsert
        upsert_tbl = Table([["id", "name"], [1, "Jane"], [5, "Bob"]])
        self.rs.upsert(upsert_tbl, f"{self.temp_schema}.test_copy", "ID")

        # Make sure that it is the expected table
        expected_tbl = Table(
            [["id", "name"], [1, "Jane"], [2, "John"], [3, "Sarah"], [5, "Bob"]]
        )
        updated_tbl = self.rs.query(
            f"select * from {self.temp_schema}.test_copy order by id;"
        )
        assert_matching_tables(expected_tbl, updated_tbl)

        # Try to run it with a bad primary key
        self.rs.query(f"INSERT INTO {self.temp_schema}.test_copy VALUES (1, 'Jim')")
        self.assertRaises(
            ValueError,
            self.rs.upsert,
            upsert_tbl,
            f"{self.temp_schema}.test_copy",
            "ID",
        )

        # Now try and upsert using two primary keys
        upsert_tbl = Table([["id", "name"], [1, "Jane"]])
        self.rs.upsert(upsert_tbl, f"{self.temp_schema}.test_copy", ["id", "name"])

        # Make sure our table looks like we expect
        expected_tbl = Table(
            [
                ["id", "name"],
                [2, "John"],
                [3, "Sarah"],
                [5, "Bob"],
                [1, "Jim"],
                [1, "Jane"],
            ]
        )
        updated_tbl = self.rs.query(
            f"select * from {self.temp_schema}.test_copy order by id;"
        )
        assert_matching_tables(expected_tbl, updated_tbl)

        # Try to run it with a bad primary key
        self.rs.query(f"INSERT INTO {self.temp_schema}.test_copy VALUES (1, 'Jim')")
        self.assertRaises(
            ValueError,
            self.rs.upsert,
            upsert_tbl,
            f"{self.temp_schema}.test_copy",
            ["ID", "name"],
        )

        self.rs.query(f"truncate table {self.temp_schema}.test_copy")

        # Run upsert with nonmatching datatypes
        upsert_tbl = Table([["id", "name"], [3, 600], [6, 9999]])
        self.rs.upsert(upsert_tbl, f"{self.temp_schema}.test_copy", "ID")

        # Make sure our table looks like we expect
        expected_tbl = Table([["id", "name"], [3, "600"], [6, "9999"]])
        updated_tbl = self.rs.query(
            f"select * from {self.temp_schema}.test_copy order by id;"
        )
        assert_matching_tables(expected_tbl, updated_tbl)

        # Run upsert requiring column resize
        upsert_tbl = Table([["id", "name"], [7, "this name is very long"]])
        self.rs.upsert(upsert_tbl, f"{self.temp_schema}.test_copy", "ID")

        # Make sure our table looks like we expect
        expected_tbl = Table(
            [["id", "name"], [3, "600"], [6, "9999"], [7, "this name is very long"]]
        )
        updated_tbl = self.rs.query(
            f"select * from {self.temp_schema}.test_copy order by id;"
        )
        assert_matching_tables(expected_tbl, updated_tbl)

    def test_unload(self):

        # Copy a table to Redshift
        self.rs.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="drop")

        # Unload a table to S3
        self.rs.unload(
            f"select * from {self.temp_schema}.test_copy",
            self.temp_s3_bucket,
            "unload_test",
        )

        # Check that files are there
        self.assertTrue(self.s3.key_exists(self.temp_s3_bucket, "unload_test"))

    def test_drop_and_unload(self):

        rs_table_test = f"{self.temp_schema}.test_copy"
        # Copy a table to Redshift
        self.rs.copy(self.tbl, rs_table_test, if_exists="drop")

        key = "unload_test"

        # Unload a table to S3
        self.rs.drop_and_unload(
            rs_table=rs_table_test,
            bucket=self.temp_s3_bucket,
            key=key,
        )

        key_prefix = f"{key}/{self.tbl.replace('.','_')}/"

        # Check that files are there
        self.assertTrue(self.s3.key_exists(self.temp_s3_bucket, key_prefix))

        self.assertFalse(self.rs.table_exists(rs_table_test))

    def test_to_from_redshift(self):

        # Test the parsons table methods
        table_name = f"{self.temp_schema}.test_copy"
        self.tbl.to_redshift(table_name, if_exists="drop")
        sql = f"SELECT * FROM {table_name} ORDER BY id"
        result_tbl = Table.from_redshift(sql)
        # Don't bother checking columns names, since those were tweaked en route to Redshift.
        assert_matching_tables(self.tbl, result_tbl, ignore_headers=True)

    def test_generate_manifest(self):

        # Add some tables to buckets
        self.tbl.to_s3_csv(
            self.temp_s3_bucket, f"{self.temp_s3_prefix}test_file_01.csv"
        )
        self.tbl.to_s3_csv(
            self.temp_s3_bucket, f"{self.temp_s3_prefix}test_file_02.csv"
        )
        self.tbl.to_s3_csv(
            self.temp_s3_bucket, f"{self.temp_s3_prefix}test_file_03.csv"
        )
        self.tbl.to_s3_csv(
            self.temp_s3_bucket, f"{self.temp_s3_prefix}dont_include.csv"
        )

        # Copy in a table to generate the headers and table
        self.rs.copy(self.tbl, f"{self.temp_schema}.test_copy", if_exists="drop")

        # Generate the manifest
        manifest_key = f"{self.temp_s3_prefix}test_manifest.json"
        manifest = self.rs.generate_manifest(
            self.temp_s3_bucket,
            prefix=f"{self.temp_s3_prefix}test_file",
            manifest_bucket=self.temp_s3_bucket,
            manifest_key=manifest_key,
        )

        # Validate path formatted correctly
        valid_url = f"s3://{self.temp_s3_bucket}/{self.temp_s3_prefix}test_file_01.csv"
        self.assertEqual(manifest["entries"][0]["url"], valid_url)

        # Validate that there are three files
        self.assertEqual(len(manifest["entries"]), 3)

        # Validate that manifest saved to bucket
        keys = self.s3.list_keys(
            self.temp_s3_bucket, prefix=f"{self.temp_s3_prefix}test_manifest"
        )
        self.assertTrue(manifest_key in keys)

    def test_move_table(self):

        # Run the method and check that new table created
        self.rs.move_table(f"{self.temp_schema}.test", f"{self.temp_schema}.test2")
        self.assertTrue(self.rs.table_exists(f"{self.temp_schema}.test2"))

        # Run the method again, but drop original
        self.rs.move_table(
            f"{self.temp_schema}.test2",
            f"{self.temp_schema}.test3",
            drop_source_table=True,
        )
        self.assertFalse(self.rs.table_exists(f"{self.temp_schema}.test2"))

    def test_get_tables(self):

        tbls_list = self.rs.get_tables(schema=self.temp_schema)
        exp = [
            "schemaname",
            "tablename",
            "tableowner",
            "tablespace",
            "hasindexes",
            "hasrules",
            "hastriggers",
        ]

        self.assertTrue(validate_list(exp, tbls_list))

    def test_get_table_stats(self):

        tbls_list = self.rs.get_table_stats(schema=self.temp_schema)

        exp = [
            "database",
            "schema",
            "table_id",
            "table",
            "encoded",
            "diststyle",
            "sortkey1",
            "max_varchar",
            "sortkey1_enc",
            "sortkey_num",
            "size",
            "pct_used",
            "empty",
            "unsorted",
            "stats_off",
            "tbl_rows",
            "skew_sortkey1",
            "skew_rows",
            "estimated_visible_rows",
            "risk_event",
            "vacuum_sort_benefit",
        ]

        # Having some issues testing that the filter is working correctly, as it
        # takes a little bit of time for a table to show in this table and is beating
        # the test suite. I feel confident that it works though.

        self.assertTrue(validate_list(exp, tbls_list))

    def test_get_views(self):
        # Assert that get_views returns filtered views

        # Assert that it works with schema filter
        views = self.rs.get_views(schema=self.temp_schema)
        expected_row = (
            self.temp_schema,
            "test_view",
            f"SELECT test.id, test.name FROM {self.temp_schema}.test;",
        )
        self.assertEqual(views.data[0], expected_row)

    def test_get_queries(self):

        # Validate that columns match expected columns
        queries_list = self.rs.get_queries()
        exp = [
            "user",
            "pid",
            "xid",
            "query",
            "service_class",
            "slot",
            "start",
            "state",
            "queue_sec",
            "exec_sec",
            "cpu_sec",
            "read_mb",
            "spill_mb",
            "return_rows",
            "nl_rows",
            "sql",
            "alert",
        ]
        self.assertTrue(validate_list(exp, queries_list))

    def test_get_row_count(self):
        table_name = f"{self.temp_schema}.test_row_count"
        self.rs.copy(self.tbl, table_name, if_exists="drop")
        count = self.rs.get_row_count(table_name)
        self.assertEqual(count, 3)

    def test_rename_table(self):

        self.rs.rename_table(self.temp_schema + ".test", "test2")

        # Test that renamed table exists
        self.assertTrue(self.rs.table_exists(self.temp_schema + ".test2"))

        # Test that old table name does not exist
        self.assertFalse(self.rs.table_exists(self.temp_schema + ".test"))

    def test_union_tables(self):

        # Copy in two tables
        self.rs.copy(self.tbl, f"{self.temp_schema}.union_base1", if_exists="drop")
        self.rs.copy(self.tbl, f"{self.temp_schema}.union_base2", if_exists="drop")

        # Union all the two tables and check row count
        self.rs.union_tables(
            f"{self.temp_schema}.union_all",
            [f"{self.temp_schema}.union_base1", f"{self.temp_schema}.union_base2"],
        )
        self.assertEqual(
            self.rs.query(f"select * from {self.temp_schema}.union_all").num_rows, 6
        )

        # Union the two tables and check row count
        self.rs.union_tables(
            f"{self.temp_schema}.union_test",
            [f"{self.temp_schema}.union_base1", f"{self.temp_schema}.union_base2"],
            union_all=False,
        )
        self.assertEqual(
            self.rs.query(f"select * from {self.temp_schema}.union_test").num_rows, 3
        )

    def test_populate_table_from_query(self):
        # Populate the source table
        source_table = f"{self.temp_schema}.test_source"
        self.rs.copy(self.tbl, source_table, if_exists="drop")

        query = f"SELECT * FROM {source_table}"

        # Populate the table
        dest_table = f"{self.temp_schema}.test_dest"
        self.rs.populate_table_from_query(query, dest_table)

        # Verify
        rows = self.rs.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]["count"], 3)

        # Try with if_exists='truncate'
        self.rs.populate_table_from_query(query, dest_table, if_exists="truncate")
        rows = self.rs.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]["count"], 3)

        # Try with if_exists='drop', and a distkey
        self.rs.populate_table_from_query(
            query, dest_table, if_exists="drop", distkey="id"
        )
        rows = self.rs.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]["count"], 3)

        # Try with if_exists='fail'
        self.assertRaises(
            ValueError,
            self.rs.populate_table_from_query,
            query,
            dest_table,
            if_exists="fail",
        )

    def test_duplicate_table(self):
        # Populate the source table
        source_table = f"{self.temp_schema}.test_source"
        self.rs.copy(self.tbl, source_table, if_exists="drop")

        # Duplicate the table
        dest_table = f"{self.temp_schema}.test_dest"
        self.rs.duplicate_table(source_table, dest_table)

        # Verify
        rows = self.rs.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]["count"], 3)

        # Try with if_exists='truncate'
        self.rs.duplicate_table(source_table, dest_table, if_exists="truncate")
        rows = self.rs.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]["count"], 3)

        # Try with if_exists='drop'
        self.rs.duplicate_table(source_table, dest_table, if_exists="drop")
        rows = self.rs.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]["count"], 3)

        # Try with if_exists='append'
        self.rs.duplicate_table(source_table, dest_table, if_exists="append")
        rows = self.rs.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]["count"], 6)

        # Try with if_exists='fail'
        self.assertRaises(
            ValueError,
            self.rs.duplicate_table,
            source_table,
            dest_table,
            if_exists="fail",
        )

        # Try with invalid if_exists arg
        self.assertRaises(
            ValueError,
            self.rs.duplicate_table,
            source_table,
            dest_table,
            if_exists="nonsense",
        )

    def test_get_max_value(self):

        date_tbl = Table(
            [["id", "date_modified"], [1, "2020-01-01"], [2, "1900-01-01"]]
        )
        self.rs.copy(date_tbl, f"{self.temp_schema}.test_date")

        # Test return string
        self.assertEqual(
            self.rs.get_max_value(f"{self.temp_schema}.test_date", "date_modified"),
            "2020-01-01",
        )

    def test_get_columns(self):
        cols = self.rs.get_columns(self.temp_schema, "test")

        # id int,name varchar(5)
        expected_cols = {
            "id": {
                "data_type": "int",
                "max_length": None,
                "max_precision": 32,
                "max_scale": 0,
                "is_nullable": True,
            },
            "name": {
                "data_type": "character varying",
                "max_length": 5,
                "max_precision": None,
                "max_scale": None,
                "is_nullable": True,
            },
        }

        self.assertEqual(cols, expected_cols)

    def test_get_object_type(self):
        # Test a table
        expected_type_table = "table"
        actual_type_table = self.rs.get_object_type("pg_catalog.pg_class")

        self.assertEqual(expected_type_table, actual_type_table)

        # Test a view
        expected_type_view = "view"
        actual_type_view = self.rs.get_object_type("pg_catalog.pg_views")

        self.assertEqual(expected_type_view, actual_type_view)

        # Test a nonexisting table
        expected_type_fake = None
        actual_type_fake = self.rs.get_object_type("someschema.faketable")

        self.assertEqual(expected_type_fake, actual_type_fake)

    def test_is_view(self):

        self.assertTrue(self.rs.is_view("pg_catalog.pg_views"))

        self.assertFalse(self.rs.is_view("pg_catalog.pg_class"))

    def test_is_table(self):

        self.assertTrue(self.rs.is_table("pg_catalog.pg_class"))

        self.assertFalse(self.rs.is_table("pg_catalog.pg_views"))

    def test_get_table_definition(self):
        expected_table_def = (
            "--DROP TABLE pg_catalog.pg_amop;"
            "\nCREATE TABLE IF NOT EXISTS pg_catalog.pg_amop"
            "\n("
            "\n\tamopclaid OID NOT NULL  ENCODE RAW"
            "\n\t,amopsubtype OID NOT NULL  ENCODE RAW"
            "\n\t,amopstrategy SMALLINT NOT NULL  ENCODE RAW"
            "\n\t,amopreqcheck BOOLEAN NOT NULL  ENCODE RAW"
            "\n\t,amopopr OID NOT NULL  ENCODE RAW"
            "\n)\nDISTSTYLE EVEN\n;"
        )
        actual_table_def = self.rs.get_table_definition("pg_catalog.pg_amop")

        self.assertEqual(expected_table_def, actual_table_def)

    def test_get_table_definitions(self):
        expected_table_defs = [
            {
                "tablename": "pg_catalog.pg_amop",
                "ddl": "--DROP TABLE pg_catalog.pg_amop;"
                "\nCREATE TABLE IF NOT EXISTS pg_catalog.pg_amop"
                "\n("
                "\n\tamopclaid OID NOT NULL  ENCODE RAW"
                "\n\t,amopsubtype OID NOT NULL  ENCODE RAW"
                "\n\t,amopstrategy SMALLINT NOT NULL  ENCODE RAW"
                "\n\t,amopreqcheck BOOLEAN NOT NULL  ENCODE RAW"
                "\n\t,amopopr OID NOT NULL  ENCODE RAW"
                "\n)\nDISTSTYLE EVEN\n;",
            },
            {
                "tablename": "pg_catalog.pg_amproc",
                "ddl": "--DROP TABLE pg_catalog.pg_amproc;"
                "\nCREATE TABLE IF NOT EXISTS pg_catalog.pg_amproc"
                "\n("
                "\n\tamopclaid OID NOT NULL  ENCODE RAW"
                "\n\t,amprocsubtype OID NOT NULL  ENCODE RAW"
                "\n\t,amprocnum SMALLINT NOT NULL  ENCODE RAW"
                "\n\t,amproc REGPROC NOT NULL  ENCODE RAW"
                "\n)"
                "\nDISTSTYLE EVEN\n;",
            },
        ]
        actual_table_defs = self.rs.get_table_definitions(table="pg_am%p%")

        self.assertEqual(expected_table_defs, actual_table_defs)

    def test_get_view_definition(self):
        expected_view_def = (
            "--DROP VIEW pg_catalog.pg_views;"
            "\nCREATE OR REPLACE VIEW pg_catalog.pg_views AS"
            "\n SELECT n.nspname AS schemaname"
            ", c.relname AS viewname"
            ", pg_get_userbyid(c.relowner) AS viewowner"
            ", pg_get_viewdef(c.oid) AS definition"
            "\n   FROM pg_class c"
            "\n   LEFT JOIN pg_namespace n ON n.oid = c.relnamespace"
            "\n  WHERE c.relkind = 'v'::\"char\";"
        )
        actual_view_def = self.rs.get_view_definition("pg_catalog.pg_views")

        self.assertEqual(expected_view_def, actual_view_def)

    def test_get_view_definitions(self):
        expected_view_defs = [
            {
                "viewname": "pg_catalog.pg_class_info",
                "ddl": "--DROP VIEW pg_catalog.pg_class_info;"
                "\nCREATE OR REPLACE VIEW pg_catalog.pg_class_info AS"
                "\n SELECT pgc.oid AS reloid, pgc.relname, pgc.relnamespace, "
                "pgc.reltype, pgc.relowner, pgc.relam, pgc.relfilenode, "
                "pgc.reltablespace, pgc.relpages, pgc.reltuples, "
                "pgc.reltoastrelid, pgc.reltoastidxid, pgc.relhasindex, "
                "pgc.relisshared, pgc.relkind, pgc.relnatts, pgc.relexternid, "
                "pgc.relisreplicated, pgc.relispinned, pgc.reldiststyle, "
                "pgc.relprojbaseid, pgc.relchecks, pgc.reltriggers, pgc.relukeys, "
                "pgc.relfkeys, pgc.relrefs, pgc.relhasoids, pgc.relhaspkey, "
                "pgc.relhasrules, pgc.relhassubclass, pgc.relacl, "
                "pgce0.value::smallint AS releffectivediststyle, "
                "date_add('microsecond'::text, pgce1.value::bigint, "
                "'2000-01-01 00:00:00'::timestamp without time zone) AS "
                "relcreationtime"
                "\n   FROM pg_class pgc"
                "\n   LEFT JOIN pg_class_extended pgce0 "
                "ON pgc.oid = pgce0.reloid AND pgce0.colnum = 0"
                "\n   LEFT JOIN pg_class_extended pgce1 "
                "ON pgc.oid = pgce1.reloid AND pgce1.colnum = 1;",
            }
        ]
        actual_view_def = self.rs.get_view_definitions(view="pg_c%")

        self.assertEqual(expected_view_defs, actual_view_def)

    def test_alter_varchar_column_widths(self):

        append_tbl = Table([["ID", "Name"], [4, "Jim"], [5, "John"], [6, "Joanna"]])

        # You can't alter column types if the table has a dependent view
        self.rs.query(f"DROP VIEW {self.temp_schema}.test_view")

        # Base table 'Name' column has a width of 5. This should expand it to 6.
        self.rs.alter_varchar_column_widths(append_tbl, f"{self.temp_schema}.test")
        self.assertEqual(
            self.rs.get_columns(self.temp_schema, "test")["name"]["max_length"], 6
        )


if __name__ == "__main__":
    unittest.main()
