import logging
from pathlib import Path
from typing import Literal

from parsons.databases.alchemy import Alchemy
from parsons.databases.database_connector import DatabaseConnector
from parsons.databases.postgres.postgres_core import PostgresCore
from parsons.databases.table import BaseTable
from parsons.etl.table import Table
from parsons.utilities import check_env

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
            If omitted or ``None``, uses ``PGPORT`` when set, otherwise 5432. If passed
            (including ``5432``), the argument takes precedence over ``PGPORT``.
        timeout: int
            Seconds to timeout if connection not established.

    """

    def __init__(self, username=None, password=None, host=None, db=None, port=None, timeout=10):
        super().__init__()

        self.username = check_env.check("PGUSER", username, optional=True)
        self.password = check_env.check("PGPASSWORD", password, optional=True)
        self.host = check_env.check("PGHOST", host, optional=True)
        self.db = check_env.check("PGDATABASE", db, optional=True)
        if port is not None:
            self.port = port
        else:
            env_port = check_env.check("PGPORT", None, optional=True)
            self.port = int(env_port) if env_port is not None else 5432

        # Check if there is a pgpass file. Psycopg2 will search for this file first when
        # creating a connection.
        pgpass = Path("~/.pgpass").expanduser().is_file()

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
        if_exists: Literal["fail", "append", "drop", "truncate"] = "fail",
        strict_length: bool = False,
    ):
        """
        Copy a :ref:`Table` to Postgres.

        Args:
            tbl: Table
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

            sql = f"""COPY "{table_name}" ("{'","'.join(tbl.columns)}") FROM STDIN CSV HEADER;"""

            with self.cursor(connection) as cursor, Path(tbl.to_csv()).open() as f:
                cursor.copy_expert(sql, f)
                logger.info(f"{tbl.num_rows} rows copied to {table_name}.")

    def table(self, table_name):
        # Return a Postgres table object

        return PostgresTable(self, table_name)


class PostgresTable(BaseTable):
    # Postgres table object.

    def max_value(self, column: str):
        """Get the max value of this column from the table."""
        return self.db.query(
            f"""
            SELECT "{column}"
            FROM {self.table}
            ORDER BY "{column}" DESC
            LIMIT 1
            """
        ).first

    def get_updated_rows(
        self,
        updated_at_column: str,
        cutoff_value,
        offset: int = 0,
        chunk_size: int | None = None,
    ) -> Table:
        """Get rows that have a greater updated_at_column value than the one provided."""
        sql = f"""
            SELECT *
            FROM {self.table}
        """
        parameters = []

        if cutoff_value is not None:
            sql += f'WHERE "{updated_at_column}" > %s'
            parameters.append(cutoff_value)

        if chunk_size:
            sql += f" LIMIT {chunk_size}"

        sql += f" OFFSET {offset}"

        result = self.db.query(sql, parameters=parameters)

        return result
