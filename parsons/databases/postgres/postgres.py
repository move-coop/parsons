from parsons.utilities import check_env
from parsons.databases.postgres.postgres_core import PostgresCore
import logging
import os


logger = logging.getLogger(__name__)


class Postgres(PostgresCore):
    """
    A Postgres class to connect to database.

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

        # Check if there is a pgpass file
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

        # To Do: Deal with not passing in a schema for the table, if I want to.

        with self.connection() as connection:

            # Auto-generate table
            if self._create_table_precheck(connection, table_name, if_exists):

                # Create the table
                # To Do: Decide which of these parameters we want to pass in.
                sql = self.create_statement(tbl, table_name, padding=None, varchar_max=None,
                                            columntypes=None)

                self.query_with_connection(sql, connection, commit=False)
                logger.info(f'{table_name} created.')

            sql = f"COPY {table_name} FROM STDIN CSV HEADER;"

            with self.cursor(connection) as cursor:
                cursor.copy_expert(sql, open(tbl.to_csv(), "r"))
                logger.info(f'{tbl.num_rows} rows copied to {table_name}.')
