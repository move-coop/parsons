import logging
import pickle
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

import petl
import psycopg2
import psycopg2.extras

from parsons.databases.postgres.postgres_create_statement import PostgresCreateStatement
from parsons.etl.table import Table
from parsons.utilities import files

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000

logger = logging.getLogger(__name__)


class PostgresCore(PostgresCreateStatement):
    @contextmanager
    def connection(self):
        """
        Generate a Postgres connection.
        The connection is set up as a python "context manager", so it will be closed
        automatically (and all queries committed) when the connection goes out of scope.

        When using the connection, make sure to put it in a ``with`` block (necessary for
        any context manager):
        ``with pg.connection() as conn:``

        Yields:
            Psycopg2 `connection` object

        """

        # Create a psycopg2 connection and cursor
        conn = psycopg2.connect(
            user=self.username,
            password=self.password,
            host=self.host,
            dbname=self.db,
            port=self.port,
            connect_timeout=self.timeout,
        )

        try:
            yield conn
        except psycopg2.Error:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def cursor(self, connection):
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            yield cur
        finally:
            cur.close()

    def query(self, sql: str, parameters: list | None = None) -> Table | None:
        """
        Execute a query against the database.

        To include python variables in your query, it is recommended to pass them as parameters,
        following the `Psycopg SQL Query Parameters Documentation <https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries>`__.
        Using the ``parameters`` argument ensures that values are escaped properly, and avoids SQL injection attacks.

        Parameter Examples:

            .. code-block:: python

                # Note that the name contains a quote,
                # which could break your query if not escaped properly.
                name = "Beatrice O'Brady"
                sql = "SELECT * FROM my_table WHERE name = %s"
                rs.query(sql, parameters=[name])

            .. code-block:: python

                names = ["Allen Smith", "Beatrice O'Brady", "Cathy Thompson"]
                placeholders = ', '.join('%s' for item in names)
                sql = f"SELECT * FROM my_table WHERE name IN ({placeholders})"
                rs.query(sql, parameters=names)

        Args:
            sql: A valid SQL statement.
            parameters: A list of python variables to be converted into SQL values in your query.

        Returns:
            Results of query.
            Will return ``None`` if the query returns zero rows.

        """

        with self.connection() as connection:
            return self.query_with_connection(sql, connection, parameters=parameters)

    def query_with_connection(self, sql, connection, parameters=None, commit=True) -> Table | None:
        """
        Execute a query against the database, with an existing connection.

        Useful for batching queries together.
        Will return ``None`` if the query returns zero rows.

        Args:
            sql: str
                A valid SQL statement
            connection: obj
                A connection object obtained from :meth:`parsons.databases.redshift.redshift.Redshift.connection`
            parameters: list
                A list of python variables to be converted into SQL values in your query
            commit: bool
                Whether to commit the transaction immediately.
                If ``False`` the transaction will be committed when the connection goes out of
                scope and is closed (or you can commit manually with ``connection.commit()``).

        """

        with self.cursor(connection) as cursor:
            logger.debug(f"SQL Query: {sql}")
            cursor.execute(sql, parameters)

            if commit:
                connection.commit()

            # If the cursor is empty, don't cause an error
            if not cursor.description:
                logger.debug("Query returned 0 rows")
                return None

            else:
                # Fetch the data in batches, and "pickle" the rows to a temp file.
                # (We pickle rather than writing to, say, a CSV, so that we maintain
                # all the type information for each field.)

                temp_file = files.create_temp_file()

                with Path(temp_file).open(mode="wb") as f:
                    # Grab the header
                    header = [i[0] for i in cursor.description]
                    pickle.dump(header, f)

                    while True:
                        batch = cursor.fetchmany(QUERY_BATCH_SIZE)
                        if not batch:
                            break

                        logger.debug(f"Fetched {len(batch)} rows.")
                        for row in batch:
                            pickle.dump(list(row), f)

                # Load a Table from the file
                final_tbl = Table(petl.frompickle(temp_file))

                logger.debug(f"Query returned {final_tbl.num_rows} rows.")
                return final_tbl

    def _create_table_precheck(
        self, connection, table_name: str, if_exists: Literal["fail", "append", "drop", "truncate"]
    ) -> bool:
        """
        Helper to determine what to do when you need a table that may already exist.

        Args:
            connection:
                A connection object obtained from :meth:`parsons.databases.redshift.redshift.Redshift.connection`.
            table_name: The table to check.
            if_exists:
                If the table already exists, either ``fail``, ``append``, ``drop``, or ``truncate`` the table.

        Returns:
            True if the table needs to be created, False otherwise.

        Raises:
            ValueError: If the `if_exists` argument has an invalid value.
            ValueError: If the table already exists and `if_exists` is set to ``fail``.

        """

        if if_exists not in ["fail", "truncate", "append", "drop"]:
            raise ValueError("Invalid value for `if_exists` argument")

        # If the table exists, evaluate the if_exists argument for next steps.
        if self.table_exists_with_connection(table_name, connection):
            if if_exists == "fail":
                raise ValueError("Table already exists.")

            if if_exists == "truncate":
                truncate_sql = f"TRUNCATE TABLE {table_name};"
                logger.info(f"Truncating {table_name}.")
                self.query_with_connection(truncate_sql, connection, commit=False)

            if if_exists == "drop":
                logger.info(f"Dropping {table_name}.")
                drop_sql = f"DROP TABLE {table_name};"
                self.query_with_connection(drop_sql, connection, commit=False)
                return True

            return False

        else:
            return True

    def table_exists(self, table_name: str, view: bool = True) -> bool:
        """
        Check if a table or view exists in the database.

        Args:
            table_name: The table name and schema (e.g. ``myschema.mytable``).
            view:
                Check to see if a view exists by the same name.
                Defaults to ``True``.

        Returns:
            ``True`` if the table exists and ``False`` if it does not.

        """
        with self.connection() as connection:
            return self.table_exists_with_connection(table_name, connection, view)

    def table_exists_with_connection(self, table_name, connection, view=True):
        # Extract the table and schema from this. If no schema is detected then
        # will default to the public schema.
        try:
            schema, table = table_name.split(".", 1)
        except ValueError:
            schema, table = "public", table_name

        with self.cursor(connection) as cursor:
            # Check in pg tables for the table
            sql = f"""select count(*) from pg_tables where schemaname='{schema}' and
                     tablename='{table}';"""

            cursor.execute(sql)
            result = cursor.fetchone()[0]

            # Check in the pg_views if it is a view
            if view:
                sql = f"""select count(*) from pg_views where schemaname='{schema}' and
                         viewname='{table}';"""
                cursor.execute(sql)
                result += cursor.fetchone()[0]

        # If in either, return boolean
        return result >= 1
