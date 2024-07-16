import logging

logger = logging.getLogger(__name__)

"""
The BaseTable class is a child class for generating a table classes that are
specific to each flavor of SQL database.
"""


class BaseTable:
    """
    Base Table class object.
    """

    def __init__(self, database_connection, table_name):

        self.table = table_name
        self.db = database_connection
        self._columns = None

    @property
    def num_rows(self):
        """
        Get the number of rows in the table.
        """

        return self.db.query(f"SELECT COUNT(*) FROM {self.table}").first

    def max_primary_key(self, primary_key):
        """
        Get the maximum primary key in the table.
        """

        return self.db.query(
            f"""
            SELECT {primary_key}
            FROM {self.table}
            ORDER BY {primary_key} DESC
            LIMIT 1
        """
        ).first

    def distinct_primary_key(self, primary_key):
        """
        Check if the passed primary key column is distinct.
        """

        sql = f"""
               SELECT
               COUNT(*) - COUNT(DISTINCT {primary_key})
               FROM {self.table}
               """

        if self.db.query(sql).first > 0:
            return False
        else:
            return True

    @property
    def columns(self):
        """
        Return a list of columns in the table.
        """

        if not self._columns:
            sql = f"SELECT * FROM {self.table} LIMIT 1"
            self._columns = self.db.query(sql).columns

        return self._columns

    @property
    def exists(self):
        """
        Check if table exists.
        """

        return self.db.table_exists(self.table)

    def get_rows(self, offset=0, chunk_size=None, order_by=None):
        """
        Get rows from a table.
        """

        sql = f"SELECT * FROM {self.table}"

        if order_by:
            sql += f" ORDER BY {order_by}"

        if chunk_size:
            sql += f" LIMIT {chunk_size}"

        sql += f" OFFSET {offset}"

        return self.db.query(sql)

    def get_new_rows_count(self, primary_key_col, start_value=None):
        """
        Get a count of rows that have a greater primary key value
        than the one provided.
        """

        sql = f"""
               SELECT
               COUNT(*)
               FROM {self.table}
               """
        params = []

        if start_value:
            sql += f"""
                    WHERE {primary_key_col} > %s
                    """
            params = [start_value]

        return self.db.query(sql, params).first

    def get_new_rows(self, primary_key, cutoff_value, offset=0, chunk_size=None):
        """
        Get rows that have a greater primary key value than the one
        provided.

        It will select every value greater than the provided value.
        """

        if cutoff_value is not None:
            where_clause = f"WHERE {primary_key} > %s"
            parameters = [cutoff_value]
        else:
            where_clause = ""
            parameters = []

        sql = f"""
               SELECT
               *
               FROM {self.table}
               {where_clause}
               ORDER BY {primary_key}
               """

        if chunk_size:
            sql += f" LIMIT {chunk_size}"

        sql += f" OFFSET {offset}"

        return self.db.query(sql, parameters)

    def drop(self, cascade=False):
        """
        Drop the table.
        """

        sql = f"DROP TABLE {self.table}"
        if cascade:
            sql += " CASCADE"

        self.db.query(sql)
        logger.info(f"{self.table} dropped.")

    def truncate(self):
        """
        Truncate the table.
        """

        self.db.query(f"TRUNCATE TABLE {self.table}")
        logger.info(f"{self.table} truncated.")
