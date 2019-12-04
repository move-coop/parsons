from parsons.utilities import check_env
from parsons.databases.postgres.postgres_core import PostgresCore
import logging
import os


logger = logging.getLogger(__name__)


class Postgres(PostgresCore):
    """
    A Postgres class to connect to database. Credentials can be passed from a ``.pgpass`` file
    stored in your home directory, environmental variables or passed arguments.

    Args:
        username: str
            Required if env variable ``PGUSERNAME`` not populated
        password: str
            Required if env variable ``PGPASSWORD`` not populated
        host: str
            Required if env variable ``PGHOST`` not populated
        db: str
            Required if env variable ``PGDB`` not populated
        port: int
            Required if env variable ``PGPORT`` not populated.
        pg_pass: str
            The path to your pg pass file
        timeout: int
            Seconds to timeout if connection not established.
    """

    def __init__(self, username=None, password=None, host=None, db=None, port=5432, timeout=10):

        # Check if there is a pgpass file. Pscopg2 will search for this file first when
        # creating a connection.
        pgpass = os.path.isfile(os.path.expanduser('~/.pgpass'))

        self.username = check_env.check('PGUSERNAME', username, pgpass)
        self.password = check_env.check('PGPASSWORD', password, pgpass)
        self.host = check_env.check('PGHOST', host, pgpass)
        self.db = check_env.check('PGDB', db, pgpass)
        self.port = check_env.check('PGPORT', port, pgpass)
        self.timeout = timeout

    def copy(self, tbl, table_name, if_exists='fail'):
        """
        Copy a :ref:`parsons-table` to Postgres.

        tbl: parsons.Table
            A Parsons table object
        table_name: str
            The destination schema and table (e.g. ``my_schema.my_table``)
        if_exists: str
            If the table already exists, either ``fail``, ``append``, ``drop``
            or ``truncate`` the table.
        """

        with self.connection() as connection:

            # Auto-generate table
            if self._create_table_precheck(connection, table_name, if_exists):

                # Create the table
                # To Do: Pass in the advanced configuration parameters.
                sql = self.create_statement(tbl, table_name)

                self.query_with_connection(sql, connection, commit=False)
                logger.info(f'{table_name} created.')

            sql = f"COPY {table_name} FROM STDIN CSV HEADER;"

            with self.cursor(connection) as cursor:
                cursor.copy_expert(sql, open(tbl.to_csv(), "r"))
                logger.info(f'{tbl.num_rows} rows copied to {table_name}.')
