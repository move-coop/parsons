from parsons import Table
from parsons.utilities import check_env
import petl
import mysql.connector as mysql
from contextlib import contextmanager
from parsons.utilities import files
import pickle
import logging
import os

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000

logger = logging.getLogger(__name__)


class MySQL():
    """
    Connect to a MySQL database.

    `Args:`
        username: str
            Required if env variable ``MYSQL_USERNAME`` not populated
        password: str
            Required if env variable ``MYSQL_PASSWORD`` not populated
        host: str
            Required if env variable ``MYSQL_HOST`` not populated
        db: str
            Required if env variable ``MYSQL_DB`` not populated
        port: int
            Can be set by env variable ``MYSQL_PORT`` or argument.
    """

    def __init__(self, host=None, username=None, password=None, db=None, port=3306):

        self.username = check_env.check('MYSQL_USERNAME', username)
        self.password = check_env.check('MYSQL_PASSWORD', password)
        self.host = check_env.check('MYSQL_HOST', host)
        # self.db = None
        self.db = check_env.check('MYSQL_DB', db)
        self.port = port or os.environ.get('MYSQL_PORT')

    @contextmanager
    def connection(self):
        """
        Generate a MySQL connection. The connection is set up as a python "context manager", so
        it will be closed automatically (and all queries committed) when the connection goes out
        of scope.

        When using the connection, make sure to put it in a ``with`` block (necessary for
        any context manager):
        ``with mysql.connection() as conn:``

        `Returns:`
            MySQL `connection` object
        """

        # Create a mysql connection and cursor
        connection = mysql.connect(host=self.host,
                                   user=self.username,
                                   passwd=self.password,
                                   database=self.db,
                                   port=self.port)

        try:
            yield connection
        except mysql.Error:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()

    @contextmanager
    def cursor(self, connection):
        cur = connection.cursor(buffered=True)

        try:
            yield cur
        finally:
            cur.close()

    def query(self, sql, parameters=None):
        """
        Execute a query against the database. Will return ``None``if the query returns zero rows.

        To include python variables in your query, it is recommended to pass them as parameters,
        following the `mysql style <https://security.openstack.org/guidelines/dg_parameterize-database-queries.html>`_.
        Using the ``parameters`` argument ensures that values are escaped properly, and avoids SQL
        injection attacks.

        **Parameter Examples**

        .. code-block:: python

            # Note that the name contains a quote, which could break your query if not escaped
            # properly.
            name = "Beatrice O'Brady"
            sql = "SELECT * FROM my_table WHERE name = %s"
            mysql.query(sql, parameters=[name])

        .. code-block:: python

            names = ["Allen Smith", "Beatrice O'Brady", "Cathy Thompson"]
            placeholders = ', '.join('%s' for item in names)
            sql = f"SELECT * FROM my_table WHERE name IN ({placeholders})"
            mysql.query(sql, parameters=names)

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
                A connection object obtained from ``mysql.connection()``
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
        with self.cursor(connection) as cursor:

            # The python connector can only execute a single sql statement, so we will
            # break up each statement and execute them separately.
            for s in sql.strip().split(';'):
                if len(s) != 0:
                    logger.debug(f'SQL Query: {sql}')
                    cursor.execute(s, parameters)

            if commit:
                connection.commit()

            # If the SQL query provides no response, then return None
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
                    pickle.dump(cursor.column_names, f)

                    while True:
                        batch = cursor.fetchmany(QUERY_BATCH_SIZE)
                        if len(batch) == 0:
                            break

                        logger.debug(f'Fetched {len(batch)} rows.')
                        for row in batch:
                            pickle.dump(row, f)

                # Load a Table from the file
                final_tbl = Table(petl.frompickle(temp_file))

                logger.debug(f'Query returned {final_tbl.num_rows} rows.')
                return final_tbl
