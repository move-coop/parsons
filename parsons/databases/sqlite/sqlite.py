import datetime
import logging
import pickle
import shutil
import sqlite3
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

import petl

from parsons.databases.database_connector import DatabaseConnector
from parsons.databases.table import BaseTable
from parsons.etl.table import Table
from parsons.utilities import files

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000

logger = logging.getLogger(__name__)


class SqliteTable(BaseTable):
    sql_placeholder = "?"

    def truncate(self) -> None:
        """Truncate the table."""
        self.db.query(f"delete from {self.table}")
        logger.info(f"{self.table} truncated.")


class Sqlite(DatabaseConnector):
    def __init__(self, db_path):
        self.db_path = db_path

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        except sqlite3.Error:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def cursor(self, connection) -> Iterator[sqlite3.Cursor]:
        cur = connection.cursor()

        try:
            yield cur
        finally:
            cur.close()

    def query(self, sql: str, parameters: list | dict | None = None) -> Table | None:
        """
        Execute a query against the database, using the existing connection within the Sqlite object.
        Will return ``None`` if the query returns zero rows.

        Args:
            sql: str
                A valid SQL statement
            parameters: list
                A list of python variables to be converted into SQL values in your query

        Returns:
            parsons.Table
                See :ref:`parsons-table` for output options.

        """
        with self.connection() as connection:
            return self.query_with_connection(sql, connection, parameters=parameters)

    def query_with_connection(
        self,
        sql: str,
        connection: sqlite3.Connection,
        parameters: list | dict | None = None,
        commit: bool = True,
        return_values: bool = True,
    ):
        """
        Execute a query against the database, with an existing connection. Useful for batching
        queries together. Will return ``None`` if the query returns zero rows.

        Args:
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

        Returns:
            parsons.Table
                See :ref:`parsons-table` for output options.

        """
        # sqlite3 cursor cannot take None for parameters
        if not parameters:
            parameters = ()

        with self.cursor(connection) as cursor:
            logger.debug(f"SQL Query: {sql}")
            cursor.execute(sql, parameters)

            if commit:
                connection.commit()

            # Fetch the data in batches, and "pickle" the rows to a temp file.
            # (We pickle rather than writing to, say, a CSV, so that we maintain
            # all the type information for each field.)

            if return_values and cursor.description:
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

    def generate_data_types(self, table: Table) -> dict[str, str]:
        """Generate column data types"""
        records = petl.records(table.table)

        type_list: dict[str, str] = {
            column: self._best_type(records, column) for column in table.columns
        }

        return type_list

    def _best_type(
        self, records: list[dict], column: str
    ) -> Literal["text", "integer", "float", "datetime", "date"]:
        values = [record[column] for record in records if record[column]]
        not_nulls = [i for i in values if i is not None]
        not_null_value = not_nulls[0] if not_nulls else None

        if isinstance(not_null_value, (int, bool)):
            result = "integer"
        elif isinstance(not_null_value, float):
            result = "float"
        elif isinstance(not_null_value, datetime.date):
            result = "date"
        elif isinstance(not_null_value, datetime.datetime):
            result = "datetime"
        else:
            result = "text"

        return result

    def create_statement(
        self,
        tbl,
        table_name,
    ) -> str:
        if tbl.num_rows == 0:
            raise ValueError("Table is empty. Must have 1 or more rows.")

        data_types = self.generate_data_types(tbl)
        result = "CREATE TABLE {} ({})".format(
            table_name,
            ", ".join(f"{column} {type}" for column, type in data_types.items()),
        )
        return result

    def copy(
        self,
        tbl: Table,
        table_name: str,
        if_exists: Literal["fail", "append", "drop", "truncate"] = "fail",
        strict_length: bool = False,
        force_python_sdk: bool = False,
    ):
        """
        Copy a :ref:`parsons-table` to Sqlite.

        Args:
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
            force_python_sdk: bool
                Use the python SDK to import data to sqlite3, even if the sqlite3 cli utility is available for more efficient loading. Defaults to False.

        """

        with self.connection() as connection:
            # Auto-generate table
            if self._create_table_precheck(connection, table_name, if_exists):
                # Create the table
                sql = self.create_statement(tbl, table_name)

                self.query_with_connection(sql, connection, commit=False, return_values=False)
                logger.info(f"{table_name} created.")

        # Use the sqlite3 command line for csv import if possible, as it is much more efficient
        if shutil.which("sqlite3") and not force_python_sdk:
            csv_file_path = tbl.to_csv()
            self._cli_command(f".import --csv --skip 1 {csv_file_path} {table_name}")
        else:
            self.import_table_iteratively(tbl, table_name, if_exists)

        logger.info(f"{len(tbl)} rows copied to {table_name}.")

    def import_table_iteratively(
        self, tbl: Table, table_name: str, if_exists: str, chunksize=10000
    ) -> None:
        """Import a CSV row by row using the python sqlite3 API.

        Iterates over chunks of length `chunksize`

        It is generally more efficient to use the sqlite3 CLI to
        import a CSV, but not all machines have the shell utility
        available, so we can fall back to this method.
        """
        chunked_tbls = tbl.chunk(chunksize)
        insert_sql = "INSERT INTO {} ({}) VALUES ({});".format(
            table_name,
            ", ".join(tbl.columns),
            ", ".join(["?" for _ in tbl.columns]),
        )
        with self.connection() as connection, self.cursor(connection) as cursor:
            for chunked_tbl in chunked_tbls:
                cursor.executemany(
                    insert_sql,
                    tuple([tuple(row.values()) for row in chunked_tbl]),
                )

    def _cli_command(self, command: str) -> None:
        """Use the sqlite3 command line utility to run a command.

        Certain commands are only possible via the shell utility and
        not via the python API, such as the CSV import command.

        sqlite3 comes as part of the python stdlib, but the shell
        utility is not available by default on all systems. Windows
        machines in particular generally don't have the sqlite3
        utility unless it is explicitly installed.
        """
        db_path = Path(self.db_path).resolve()
        full_command = ["sqlite3", str(db_path), command]
        resp = subprocess.run(
            full_command,
            capture_output=True,
        )
        if resp.stderr:
            raise RuntimeError(resp.stderr.decode())
        if resp.returncode:
            raise RuntimeError(resp.stdout.decode())

    def _create_table_precheck(
        self, connection, table_name, if_exists: Literal["fail", "append", "drop", "truncate"]
    ) -> bool:
        """
        Helper to determine what to do when you need a table that may already exist.

        Args:
            connection: obj
                A connection object obtained from ``redshift.connection()``
            table_name: str
                The table to check
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``,
                or ``truncate`` the table.

        Returns:
            bool
                True if the table needs to be created, False otherwise.

        """

        if if_exists not in ["fail", "truncate", "append", "drop"]:
            raise ValueError("Invalid value for `if_exists` argument")

        # If the table exists, evaluate the if_exists argument for next steps.
        if self.table_exists(table_name):
            if if_exists == "fail":
                raise ValueError("Table already exists.")

            if if_exists == "truncate":
                truncate_sql = f"DELETE FROM {table_name};"
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

    def table_exists(self, table_name: str, view: bool = False) -> bool:
        """
        Check if a table or view exists in the database.

        Args:
            table_name: str
                The table name and schema (e.g. ``myschema.mytable``).
            view: boolean
                Check to see if a view exists by the same name. Defaults to ``False``.

        Returns:
            boolean
                ``True`` if the table exists and ``False`` if it does not.

        """
        # Check in pg tables for the table
        sql = "select name from sqlite_master where type=:type and name = :name"
        result = self.query(
            sql, parameters={"type": "view" if view else "table", "name": table_name}
        )

        # If in either, return boolean
        return bool(result)

    def table(self, table_name: str) -> SqliteTable:
        # Return a Sqlite table instance
        return SqliteTable(self, table_name)
