from parsons.databases.postgres.postgres_core import PostgresCore
from parsons.databases.table import BaseTable
from parsons.databases.alchemy import Alchemy
from parsons.databases.database_connector import DatabaseConnector
from parsons.etl.table import Table
import logging
import os


logger = logging.getLogger(__name__)


class Postgres(PostgresCore, Alchemy, DatabaseConnector):
    """
    A Postgres class to connect to database. Credentials can be passed from a ``.pgpass`` file
    stored in your home directory or with environmental variables.

    Args:
        username: str
            Required if env variable ``PGUSER`` not populated
        password: str
            Required if env variable ``PGPASSWORD`` not populated
        host: str
            Required if env variable ``PGHOST`` not populated
        db: str
            Required if env variable ``PGDATABASE`` not populated
        port: int
            Required if env variable ``PGPORT`` not populated.
        timeout: int
            Seconds to timeout if connection not established.
    """

    def __init__(self, username=None, password=None, host=None, db=None, port=5432, timeout=10):
        super().__init__()

        self.username = username or os.environ.get("PGUSER")
        self.password = password or os.environ.get("PGPASSWORD")
        self.host = host or os.environ.get("PGHOST")
        self.db = db or os.environ.get("PGDATABASE")
        self.port = port or os.environ.get("PGPORT")

        # Check if there is a pgpass file. Psycopg2 will search for this file first when
        # creating a connection.
        pgpass = os.path.isfile(os.path.expanduser("~/.pgpass"))

        if not any([self.username, self.password, self.host, self.db]) and not pgpass:
            raise ValueError(
                "Connection arguments missing. Please pass as a pgpass file, kwargs",
                "or env variables.",
            )

        self.timeout = timeout
        self.dialect = "postgres"

    def copy(
        self,
        tbl: Table,
        table_name: str,
        if_exists: str = "fail",
        strict_length: bool = False,
    ):
        """
        Copy a :ref:`parsons-table` to Postgres.

        `Args:`
            tbl: parsons.Table
                A Parsons table object
            table_name: str
                The destination schema and table (e.g. ``my_schema.my_table``)
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            strict_length: bool
                If the database table needs to be created, strict_length determines whether
                the created table's column sizes will be sized to exactly fit the current data,
                or if their size will be rounded up to account for future values being larger
                then the current dataset. Defaults to ``False``.
        """

        with self.connection() as connection:
            # Auto-generate table
            if self._create_table_precheck(connection, table_name, if_exists):
                # Create the table
                # To Do: Pass in the advanced configuration parameters.
                sql = self.create_statement(tbl, table_name, strict_length=strict_length)

                self.query_with_connection(sql, connection, commit=False)
                logger.info(f"{table_name} created.")

            sql = f"COPY {table_name} FROM STDIN CSV HEADER;"

            with self.cursor(connection) as cursor:
                cursor.copy_expert(sql, open(tbl.to_csv(), "r"))
                logger.info(f"{tbl.num_rows} rows copied to {table_name}.")

    def table(self, table_name):
        # Return a Postgres table object

        return PostgresTable(self, table_name)


class PostgresTable(BaseTable):
    # Postgres table object.

    pass
