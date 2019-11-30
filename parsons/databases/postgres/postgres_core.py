from contextlib import contextmanager
import psycopg2
import psycopg2.extras
from parsons.etl.table import Table
from parsons.utilities import files
import pickle
import petl
import logging

from parsons.databases.redshift.rs_create_table import RedshiftCreateTable # Temporary
from parsons.databases.redshift.rs_table_utilities import RedshiftTableUtilities # Temporary

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000

logger = logging.getLogger(__name__)


# To Do: Might want to rename the subclasses to Postgres at some point in the future. Also
# need to test them to see if all of the methods work with Postgres.

class PostgresCore(RedshiftCreateTable, RedshiftTableUtilities):

    @contextmanager
    def connection(self):
        """
        Generate a Postgres connection.
        The connection is set up as a python "context manager", so it will be closed
        automatically (and all queries committed) when the connection goes out of scope.

        When using the connection, make sure to put it in a ``with`` block (necessary for
        any context manager):
        ``with pg.connection() as conn:``

        `Returns:`
            Psycopg2 `connection` object
        """

        # Create a psycopg2 connection and cursor
        conn = psycopg2.connect(user=self.username, password=self.password,
                                host=self.host, dbname=self.db, port=self.port,
                                connect_timeout=self.timeout)
        yield conn

        conn.commit()
        conn.close()

    @contextmanager
    def cursor(self, connection):
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        yield cur
        cur.close()

    def query(self, sql, parameters=None):
        """
        Execute a query against the database. Will return ``None``if the query returns zero rows.

        To include python variables in your query, it is recommended to pass them as parameters,
        following the `psycopg style <http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries>`_.
        Using the ``parameters`` argument ensures that values are escaped properly, and avoids SQL
        injection attacks.

        **Parameter Examples**

        .. code-block:: python

            # Note that the name contains a quote, which could break your query if not escaped
            # properly.
            name = "Beatrice O'Brady"
            sql = "SELECT * FROM my_table WHERE name = %s"
            rs.query(sql, parameters=[name])

        .. code-block:: python

            names = ["Allen Smith", "Beatrice O'Brady", "Cathy Thompson"]
            placeholders = ', '.join('%s' for item in names)
            sql = f"SELECT * FROM my_table WHERE name IN ({placeholders})"
            rs.query(sql, parameters=names)

        `Args:`
            sql: str
                A valid SQL statement
            parameters: list
                A list of python variables to be converted into SQL values in your query

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.

        """  # noqa: E501

        with self.connection() as connection:
            return self.query_with_connection(sql, connection, parameters=parameters)

    def query_with_connection(self, sql, connection, parameters=None, commit=True):
        """
        Execute a query against the database, with an existing connection. Useful for batching
        queries together. Will return ``None`` if the query returns zero rows.

        `Args:`
            sql: str
                A valid SQL statement
            connection: obj
                A connection object obtained from ``redshift.connection()``
            parameters: list
                A list of python variables to be converted into SQL values in your query
            commit: boolean
                Whether to commit the transaction immediately. If ``False`` the transaction will
                be committed when the connection goes out of scope and is closed (or you can
                commit manually with ``connection.commit()``).

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        # To Do: Have it return an ordered dict to return the
        #        rows in the correct order

        with self.cursor(connection) as cursor:

            logger.debug(f'SQL Query: {sql}')
            cursor.execute(sql, parameters)

            if commit:
                connection.commit()

            # If the cursor is empty, don't cause an error
            if not cursor.description:
                logger.debug('Query returned 0 rows')
                return None

            else:

                # Fetch the data in batches, and "pickle" the rows to a temp file.
                # (We pickle rather than writing to, say, a CSV, so that we maintain
                # all the type information for each field.)

                temp_file = files.create_temp_file()

                with open(temp_file, 'wb') as f:
                    # Grab the header
                    header = [i[0] for i in cursor.description]
                    pickle.dump(header, f)

                    while True:
                        batch = cursor.fetchmany(QUERY_BATCH_SIZE)
                        if not batch:
                            break

                        logger.debug(f'Fetched {len(batch)} rows.')
                        for row in batch:
                            pickle.dump(list(row), f)

                # Load a Table from the file
                final_tbl = Table(petl.frompickle(temp_file))

                logger.debug(f'Query returned {final_tbl.num_rows} rows.')
                return final_tbl