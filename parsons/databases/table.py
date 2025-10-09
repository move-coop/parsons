import logging
import datetime

logger = logging.getLogger(__name__)

"""
The BaseTable class is a child class for generating a table classes that are
specific to each flavor of SQL database.
"""


class BaseTable:
    """
    Base Table class object.
    """

    sql_placeholder: str = "%s"

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

        return not self.db.query(sql).first > 0

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

        if offset:
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
                    WHERE {primary_key_col} > {self.sql_placeholder}
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
            where_clause = f"WHERE {primary_key} > {self.sql_placeholder}"
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

    def dedup_table(
        self,
        order_by_column_name=None,
        order_by_direction=None,
        cascade=False,
        columns_to_ignore=None,
    ):
        """
        Description:
            This function re-creates a deduped version of a table by grabbing
            all columns and inserting those into a partition statement for
            row_number().
        Args:
            order_by_column_name: str (optional)
                Column name of specific column that you would like to dedup using order by
            order_by_direction: str (optional)
                Order by direction, if you would like to dedup by ordering by a specific column,
                this is the direction of the order by
                example: 'asc'
            cascade: bool (optional)
                Set to True if you want any dependent views to be dropped -
                queries will fail if there are dependent views and this is set to False.
           columns_to_ignore: list (optional)
                List any columns that should be ignored in the dedup
        """
        current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        run_cascade = "CASCADE" if cascade else ""
        order_by_column_name = "random()" if order_by_column_name is None else order_by_column_name
        if order_by_direction is None and order_by_column_name is not None:
            raise Exception("order_by_direction argument is blank")

        columns_list = self.columns

        # remove order_by columns
        columns_list.remove(order_by_column_name) if order_by_column_name is not None else None

        # remove ignore columns
        if columns_to_ignore is not None:
            for column in columns_to_ignore:
                columns_list.remove(column)

        partition = ", ".join(columns_list)

        dedup_query = f"""
            create table {self.table}_temp_{current_timestamp} as
            (select *
            , row_number() over (partition by {partition}
            order by {order_by_column_name} {order_by_direction}) as dup
            from {self.table})
            where dup=1;
            alter table {self.table}_temp_{current_timestamp}
            drop column dup;
            truncate table {self.table};
            insert into {self.table} (select * from {self.table}_temp_{current_timestamp})
            {run_cascade};
            drop view {self.table}_temp_{current_timestamp}
        """

        self.db.query(dedup_query)
        logger.info(f"Finished deduping {self.table}...")

        return None
