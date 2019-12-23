import logging

logger = logging.getLogger(__name__)


def table_factory(database_connection, table_name):
    """
    Generate Table objects specific to the SQL dialect.
    """

    if database_connection.dialect in ['postgres', 'redshift']:

        return PostgresTable(database_connection, table_name)

    if database_connection in ['bigquery']:

        return BigQueryTable(database_connection, table_name)

    else:
        raise ValueError('Invalid database connection object.')


class BaseTable:

    def __init__(self, database_connection, table_name):

        self.table = table_name
        self.connection = database_connection

    @property
    def num_rows(self):
        """
        Get the number of rows in the table.
        """

        return self.connection.query(f"SELECT COUNT(*) FROM {self.table};").first

    def max_primary_key(self, primary_key):
        """
        Get the maximum primary key in the table.
        """

        return self.connection.query(f"SELECT MAX({primary_key}) FROM {self.table};").first

    @property
    def exists(self):

        return self.connection.table_exists(self.table)

    def get_rows(self, offset=0, chunk_size=None):
        """
        Get rows from a table.
        """

        sql = f"SELECT * FROM {self.table} OFFSET {offset}"

        if chunk_size:
            sql += f" LIMIT {chunk_size};"

        return self.connection.query(sql)

    def get_new_rows_count(self, primary_key_col, max_value):
        """
        Get a count of rows that have a greater primary key value
        than the one provided.
        """

        sql = f"""SELECT
                  COUNT(*)
                  FROM {self.table}
                  WHERE {primary_key_col} > {max_value};
               """

        return self.connection.query(sql).first

    def get_new_rows(self, primary_key_col, max_value, offset=0, chunk_size=None):
        """
        Get rows that have a greater primary key value than the one
        provided.
        """

        sql = f"""SELECT
                  *
                  FROM {self.table}
                  WHERE {primary_key_col} > {max_value}
               """

        if chunk_size:
            sql += f" LIMIT {chunk_size};"

        return self.connection.query(sql)

    def drop(self, cascade=False):
        """
        Drop a table.
        """

        sql = f'DROP TABLE {self.table}'
        if cascade:
            sql += ' CASCADE;'

        self.connection.query(sql)
        logger.info(f'{self.table} dropped.')

    def truncate(self):
        """
        Truncate a table.
        """

        self.connection.query(f'TRUNCATE TABLE {self.table};')
        logger.info(f'{self.table} dropped.')


class BigQueryTable(BaseTable):

    def drop(self):

        self.delete_table()

class PostgresTable(BaseTable):

      pass
