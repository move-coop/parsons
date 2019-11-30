from parsons import Postgres
from parsons.etl.table import Table
from test.utils import assert_matching_tables
import unittest
import os
import re
import warnings
import datetime
from test.utils import validate_list

# The name of the schema and will be temporarily created for the tests
TEMP_SCHEMA = 'parsons_test'

# These tests do not interact with the Postgres Database directly, and don't need real credentials


class TestPostgres(unittest.TestCase):

    def setUp(self):

        self.pg = Postgres(username='test', password='test', host='test', db='test', port=123)

        self.tbl = Table([['ID', 'Name'],
                          [1, 'Jim'],
                          [2, 'John'],
                          [3, 'Sarah']])

        self.mapping = self.pg.generate_data_types(self.tbl)

    def test_data_type(self):

        # Test smallint
        self.assertEqual(self.pg.data_type(1, ''), 'smallint')
        # Test int
        self.assertEqual(self.pg.data_type(32769, ''), 'int')
        # Test bigint
        self.assertEqual(self.pg.data_type(2147483648, ''), 'bigint')
        # Test varchar that looks like an int
        self.assertEqual(self.pg.data_type('00001', ''), 'varchar')
        # Test a float as a decimal
        self.assertEqual(self.pg.data_type(5.001, ''), 'decimal')
        # Test varchar
        self.assertEqual(self.pg.data_type('word', ''), 'varchar')
        # Test int with underscore
        self.assertEqual(self.pg.data_type('1_2', ''), 'varchar')
        # Test int with leading zero
        self.assertEqual(self.pg.data_type('01', ''), 'varchar')

    def test_generate_data_types(self):

        # Test correct header labels
        self.assertEqual(self.mapping['headers'], ['ID', 'Name'])
        # Test correct data types
        self.assertEqual(self.mapping['type_list'], ['smallint', 'varchar'])
        # Test correct lengths
        self.assertEqual(self.mapping['longest'], [1, 5])

    def test_vc_padding(self):

        # Test padding calculated correctly
        self.assertEqual(self.pg.vc_padding(self.mapping, .2), [1, 6])

    def test_vc_max(self):

        # Test max sets it to the max
        self.assertEqual(self.pg.vc_max(self.mapping, ['Name']), [1, 65535])

        # Test raises when can't find column
        # To Do

    def test_vc_validate(self):

        # Test that a column with a width of 0 is set to 1
        self.mapping['longest'][0] = 0
        self.mapping = self.pg.vc_validate(self.mapping)
        self.assertEqual(self.mapping, [1, 5])

    def test_create_sql(self):

        # Test the the statement is expected
        sql = self.pg.create_sql('tmc.test', self.mapping, distkey='ID')
        exp_sql = "create table tmc.test (\n  id smallint,\n  name varchar(5)) \ndistkey(ID) ;"
        self.assertEqual(sql, exp_sql)

    def test_column_validate(self):

        bad_cols = ['', 'SELECT', 'asdfjkasjdfklasjdfklajskdfljaskldfjaklsdfjlaksdfjklasjdfklasjdkfljaskldfljkasjdkfasjlkdfjklasdfjklakjsfasjkdfljaslkdfjklasdfjklasjkldfakljsdfjalsdkfjklasjdfklasjdfklasdkljf'] # noqa: E501
        fixed_cols = ['col_0', 'col_1', 'asdfjkasjdfklasjdfklajskdfljaskldfjaklsdfjlaksdfjklasjdfklasjdkfljaskldfljkasjdkfasjlkdfjklasdfjklakjsfasjkdfljaslkdfjkl'] # noqa: E501
        self.assertEqual(self.pg.column_name_validate(bad_cols), fixed_cols)

    def test_create_statement(self):

        # Assert that copy statement is expected
        sql = self.pg.create_statement(self.tbl, 'tmc.test', distkey='ID')
        exp_sql = """create table tmc.test (\n  "id" smallint,\n  "name" varchar(5)) \ndistkey(ID) ;"""  # noqa: E501
        self.assertEqual(sql, exp_sql)

        # Assert that an error is raised by an empty table
        empty_table = Table([['Col_1', 'Col_2']])
        self.assertRaises(ValueError, self.pg.create_statement, empty_table, 'tmc.test')

# These tests interact directly with the Postgres database

@unittest.skipIf(not os.environ.get('LIVE_TEST'), 'Skipping because not running live test')
class TestPostgresDB(unittest.TestCase):

    def setUp(self):

        self.temp_schema = TEMP_SCHEMA

        self.pg = Postgres()

        self.tbl = Table([['ID', 'Name'],
                          [1, 'Jim'],
                          [2, 'John'],
                          [3, 'Sarah']])

        # Create a schema, create a table, create a view
        setup_sql = f"""
                    drop schema if exists {self.temp_schema} cascade;
                    create schema {self.temp_schema};
                    """

        other_sql = f"""
                    create table {self.temp_schema}.test (id smallint,name varchar(5));
                    create view {self.temp_schema}.test_view as (select * from {self.temp_schema}.test);
                    """ # noqa: E501

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
        r = self.pg.query('select 1')
        self.assertEqual(r[0]['?column?'], 1)

    def test_query_with_parameters(self):
        table_name = f"{self.temp_schema}.test"
        self.pg.copy(self.tbl, f"{self.temp_schema}.test", if_exists='append')

        sql = f"select * from {table_name} where name = %s"
        name = 'Sarah'
        r = self.pg.query(sql, parameters=[name])
        self.assertEqual(r[0]['name'], name)

        sql = f"select * from {table_name} where name in (%s, %s)"
        names = ['Sarah', 'John']
        r = self.pg.query(sql, parameters=names)
        self.assertEqual(r.num_rows, 2)

    """
    def test_schema_exists(self):
        self.assertTrue(self.pg.schema_exists(self.temp_schema))
        self.assertFalse(self.pg.schema_exists('nonsense'))
    """

    """
    def test_table_exists(self):

        # Check if table_exists finds a table that exists
        self.assertTrue(self.pg.table_exists(f'{self.temp_schema}.test'))

        # Check if table_exists is case insensitive
        self.assertTrue(self.pg.table_exists(f'{self.temp_schema.upper()}.TEST'))

        # Check if table_exists doesn't find a table that doesn't exists
        self.assertFalse(self.pg.table_exists(f'{self.temp_schema}.test_fake'))

        # Check if table_exists finds a table that exists
        self.assertTrue(self.pg.table_exists(f'{self.temp_schema}.test_view'))

        # Check if table_exists doesn't find a view that doesn't exists
        self.assertFalse(self.pg.table_exists(f'{self.temp_schema}.test_view_fake'))

        # Check that the view kwarg works
        self.assertFalse(self.pg.table_exists(f'{self.temp_schema}.test_view', view=False))
    """

    def test_copy(self):

        # Copy a table
        self.pg.copy(self.tbl, f'{self.temp_schema}.test_copy', if_exists='drop')

        # Test that file exists
        r = self.pg.query(f"select * from {self.temp_schema}.test_copy where name='Jim'")
        self.assertEqual(r[0]['id'], 1)

        # Copy to the same table, to verify that the "truncate" flag works.
        self.pg.copy(self.tbl, f'{self.temp_schema}.test_copy', if_exists='truncate')
        rows = self.pg.query(f"select count(*) from {self.temp_schema}.test_copy")
        self.assertEqual(rows[0]['count'], 3)

        # Copy to the same table, to verify that the "drop" flag works.
        self.pg.copy(self.tbl, f'{self.temp_schema}.test_copy', if_exists='drop')

    """
    def test_move_table(self):

        # Run the method and check that new table created
        self.pg.move_table(f'{self.temp_schema}.test', f'{self.temp_schema}.test2')
        self.assertTrue(self.pg.table_exists(f'{self.temp_schema}.test2'))

        # Run the method again, but drop original
        self.pg.move_table(f'{self.temp_schema}.test2', f'{self.temp_schema}.test3',
                                drop_source_table=True)
        self.assertFalse(self.pg.table_exists(f'{self.temp_schema}.test2'))
    """

    """
    def test_get_tables(self):

        tbls_list = self.pg.get_tables(schema=self.temp_schema)
        exp = ['schemaname', 'tablename', 'tableowner', 'tablespace', 'hasindexes',
               'hasrules', 'hastriggers']

        self.assertTrue(validate_list(exp, tbls_list))
    """

    """
    def test_get_table_stats(self):

        tbls_list = self.pg.get_table_stats(schema=self.temp_schema)
        exp = ['database', 'schema', 'table_id', 'table', 'encoded', 'diststyle', 'sortkey1',
               'max_varchar', 'sortkey1_enc', 'sortkey_num', 'size', 'pct_used', 'empty',
               'unsorted', 'stats_off', 'tbl_rows', 'skew_sortkey1', 'skew_rows']

        # Having some issues testing that the filter is working correctly, as it
        # takes a little bit of time for a table to show in this table and is beating
        # the test suite. I feel confident that it works though.

        self.assertTrue(validate_list(exp, tbls_list))
    """

    """
    def test_get_views(self):
        # Assert that get_views returns filtered views

        # Assert that it works with schema filter
        views = self.pg.get_views(schema=self.temp_schema)
        expected_row = (self.temp_schema,
                        'test_view',
                        f'SELECT test.id, test.name FROM {self.temp_schema}.test;')
        self.assertEqual(views.data[0], expected_row)
    """

    """
    def test_get_queries(self):

        # Validate that columns match expected columns
        queries_list = self.pg.get_queries()
        exp = ['user', 'pid', 'xid', 'query', 'service_class', 'slot', 'start', 'state',
               'queue_sec', 'exec_sec', 'cpu_sec', 'read_mb', 'spill_mb', 'return_rows',
               'nl_rows', 'sql', 'alert']
        self.assertTrue(validate_list(exp, queries_list))
    """

    """
    def test_get_row_count(self):
        table_name = f'{self.temp_schema}.test_row_count'
        self.pg.copy(self.tbl, table_name, if_exists='drop')
        count = self.pg.get_row_count(table_name)
        self.assertEqual(count, 3)
    """

    """
    def test_rename_table(self):

        self.pg.rename_table(self.temp_schema + '.test', 'test2')

        # Test that renamed table exists
        self.assertTrue(self.pg.table_exists(self.temp_schema + '.test2'))

        # Test that old table name does not exist
        self.assertFalse(self.pg.table_exists(self.temp_schema + '.test'))
    """

    """
    def test_union_tables(self):

        # Copy in two tables
        self.pg.copy(self.tbl, f'{self.temp_schema}.union_base1', if_exists='drop')
        self.pg.copy(self.tbl, f'{self.temp_schema}.union_base2', if_exists='drop')

        # Union all the two tables and check row count
        self.pg.union_tables(f'{self.temp_schema}.union_all',
                             [f'{self.temp_schema}.union_base1', f'{self.temp_schema}.union_base2'])
        self.assertEqual(self.pg.query(f"select * from {self.temp_schema}.union_all").num_rows, 6)

        # Union the two tables and check row count
        self.pg.union_tables(f'{self.temp_schema}.union_test',
                             [f'{self.temp_schema}.union_base1', f'{self.temp_schema}.union_base2'],
                             union_all=False)
        self.assertEqual(self.pg.query(f"select * from {self.temp_schema}.union_test").num_rows, 3)
    """

    """
    def test_populate_table_from_query(self):
        # Populate the source table
        source_table = f'{self.temp_schema}.test_source'
        self.pg.copy(self.tbl, source_table, if_exists='drop')

        query = f"SELECT * FROM {source_table}"

        # Populate the table
        dest_table = f'{self.temp_schema}.test_dest'
        self.pg.populate_table_from_query(query, dest_table)

        # Verify
        rows = self.pg.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]['count'], 3)

        # Try with if_exists='truncate'
        self.pg.populate_table_from_query(query, dest_table, if_exists='truncate')
        rows = self.pg.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]['count'], 3)

        # Try with if_exists='drop'
        self.pg.populate_table_from_query(query, dest_table, if_exists='drop')
        rows = self.pg.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]['count'], 3)

        # Try with if_exists='fail'
        self.assertRaises(ValueError,
            self.pg.populate_table_from_query, query, dest_table, if_exists='fail')

    def test_duplicate_table(self):
        # Populate the source table
        source_table = f'{self.temp_schema}.test_source'
        self.pg.copy(self.tbl, source_table, if_exists='drop')

        # Duplicate the table
        dest_table = f'{self.temp_schema}.test_dest'
        self.pg.duplicate_table(source_table, dest_table)

        # Verify
        rows = self.pg.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]['count'], 3)

        # Try with if_exists='truncate'
        self.pg.duplicate_table(source_table, dest_table, if_exists='truncate')
        rows = self.pg.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]['count'], 3)

        # Try with if_exists='drop'
        self.pg.duplicate_table(source_table, dest_table, if_exists='drop')
        rows = self.pg.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]['count'], 3)

        # Try with if_exists='append'
        self.pg.duplicate_table(source_table, dest_table, if_exists='append')
        rows = self.pg.query(f"select count(*) from {dest_table}")
        self.assertEqual(rows[0]['count'], 6)

        # Try with if_exists='fail'
        self.assertRaises(ValueError, self.pg.duplicate_table, source_table,
                          dest_table, if_exists='fail')

        # Try with invalid if_exists arg
        self.assertRaises(ValueError, self.pg.duplicate_table, source_table,
                          dest_table, if_exists='nonsense')
    """

    """
    def test_get_max_value(self):

        date_tbl = Table([['id', 'date_modified'], [1, '2020-01-01'], [2, '1900-01-01']])
        self.pg.copy(date_tbl, f'{self.temp_schema}.test_date')

        # Test return string
        self.assertEqual(self.pg.get_max_value(f'{self.temp_schema}.test_date', 'date_modified'),
                         '2020-01-01')
    """

    """
    def test_get_columns(self):
        cols = self.pg.get_columns(self.temp_schema, 'test')

        # id smallint,name varchar(5)
        expected_cols = {
            'id':   {
                'data_type': 'smallint', 'max_length': 16,
                'max_precision': None, 'max_scale': None, 'is_nullable': True},
            'name': {
                'data_type': 'character varying', 'max_length': 5,
                'max_precision': None, 'max_scale': None, 'is_nullable': True},
        }

        self.assertEqual(cols, expected_cols)
    """

    """
    def test_get_object_type(self):
        # Test a table
        expected_type_table = "table"
        actual_type_table = self.pg.get_object_type("pg_catalog.pg_class")

        self.assertEqual(expected_type_table, actual_type_table)

        # Test a view
        expected_type_view = "view"
        actual_type_view = self.pg.get_object_type("pg_catalog.pg_views")

        self.assertEqual(expected_type_view, actual_type_view)

        # Test a nonexisting table
        expected_type_fake = None
        actual_type_fake = self.pg.get_object_type("someschema.faketable")

        self.assertEqual(expected_type_fake, actual_type_fake)
    """

    """
    def test_is_view(self):

        self.assertTrue(self.pg.is_view("pg_catalog.pg_views"))

        self.assertFalse(self.pg.is_view("pg_catalog.pg_class"))
    """

    """
    def test_is_table(self):

        self.assertTrue(self.pg.is_table("pg_catalog.pg_class"))

        self.assertFalse(self.pg.is_table("pg_catalog.pg_views"))
    """

    """
    def test_get_table_definition(self):
        expected_table_def = (
            '--DROP TABLE pg_catalog.pg_amop;'
            '\nCREATE TABLE IF NOT EXISTS pg_catalog.pg_amop'
            '\n('
            '\n\tamopclaid OID NOT NULL  ENCODE RAW'
            '\n\t,amopsubtype OID NOT NULL  ENCODE RAW'
            '\n\t,amopstrategy SMALLINT NOT NULL  ENCODE RAW'
            '\n\t,amopreqcheck BOOLEAN NOT NULL  ENCODE RAW'
            '\n\t,amopopr OID NOT NULL  ENCODE RAW'
            '\n)\nDISTSTYLE EVEN\n;')
        actual_table_def = self.pg.get_table_definition("pg_catalog.pg_amop")

        self.assertEqual(expected_table_def, actual_table_def)
    """

    """
    def test_get_table_definitions(self):
        expected_table_defs = [{
            'tablename': 'pg_catalog.pg_amop',
            'ddl': '--DROP TABLE pg_catalog.pg_amop;'
                   '\nCREATE TABLE IF NOT EXISTS pg_catalog.pg_amop'
                   '\n('
                   '\n\tamopclaid OID NOT NULL  ENCODE RAW'
                   '\n\t,amopsubtype OID NOT NULL  ENCODE RAW'
                   '\n\t,amopstrategy SMALLINT NOT NULL  ENCODE RAW'
                   '\n\t,amopreqcheck BOOLEAN NOT NULL  ENCODE RAW'
                   '\n\t,amopopr OID NOT NULL  ENCODE RAW'
                   '\n)\nDISTSTYLE EVEN\n;'}, {
            'tablename': 'pg_catalog.pg_amproc',
            'ddl': '--DROP TABLE pg_catalog.pg_amproc;'
                   '\nCREATE TABLE IF NOT EXISTS pg_catalog.pg_amproc'
                   '\n('
                   '\n\tamopclaid OID NOT NULL  ENCODE RAW'
                   '\n\t,amprocsubtype OID NOT NULL  ENCODE RAW'
                   '\n\t,amprocnum SMALLINT NOT NULL  ENCODE RAW'
                   '\n\t,amproc REGPROC NOT NULL  ENCODE RAW'
                   '\n)'
                   '\nDISTSTYLE EVEN\n;'}]
        actual_table_defs = self.pg.get_table_definitions(table="pg_am%p%")

        self.assertEqual(expected_table_defs, actual_table_defs)
    """

    """
    def test_get_view_definition(self):
        expected_view_def = (
            '--DROP VIEW pg_catalog.pg_views;'
            '\nCREATE OR REPLACE VIEW pg_catalog.pg_views AS'
            '\n SELECT n.nspname AS schemaname'
            ', c.relname AS viewname'
            ', pg_get_userbyid(c.relowner) AS viewowner'
            ', pg_get_viewdef(c.oid) AS definition'
            '\n   FROM pg_class c'
            '\n   LEFT JOIN pg_namespace n ON n.oid = c.relnamespace'
            '\n  WHERE c.relkind = \'v\'::"char";')
        actual_view_def = self.pg.get_view_definition("pg_catalog.pg_views")

        self.assertEqual(expected_view_def, actual_view_def)
    """

    """
    def test_get_view_definitions(self):
        expected_view_defs = [{
            'viewname': 'pg_catalog.pg_class_info',
            'ddl': "--DROP VIEW pg_catalog.pg_class_info;"
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
            "ON pgc.oid = pgce1.reloid AND pgce1.colnum = 1;"}]
        actual_view_def = self.pg.get_view_definitions(view="pg_c%")

        self.assertEqual(expected_view_defs, actual_view_def)
    """

if __name__ == "__main__":
    unittest.main()
