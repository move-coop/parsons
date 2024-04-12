import datetime
import logging
from typing import Literal, Union

from parsons.databases.database_connector import DatabaseConnector
from parsons.etl.table import Table

logger = logging.getLogger(__name__)


class DBSync:
    """
    Sync tables between databases. Works with ``Postgres``, ``Redshift``, ``MySQL``
    databases.

    `Args:`
        source_db: Database connection object
            A database object.
        destination_db: Database connection object
            A database object.
        read_chunk_size: int
            The number of rows to read from the source at a time when syncing a table. The
            default value is 100,000 rows.
        write_chunk_size: int
            The number of rows to batch up before writing out to the destination. This value
            defaults to whatever the read_chunk_size is.
        retries: int
            The number of times to retry if there is an error processing a
            chunk of data. The default value is 0.
    `Returns:`
        A DBSync object.
    """

    def __init__(
        self,
        source_db: DatabaseConnector,
        destination_db: DatabaseConnector,
        read_chunk_size: int = 100_000,
        write_chunk_size: int = None,
        retries: int = 0,
    ):

        self.source_db = source_db
        self.dest_db = destination_db
        self.read_chunk_size = read_chunk_size
        self.write_chunk_size = write_chunk_size or read_chunk_size
        self.retries = retries

    def table_sync_full(
        self,
        source_table,
        destination_table,
        if_exists="drop",
        order_by=None,
        verify_row_count=True,
        **kwargs,
    ):
        """
        Full sync of table from a source database to a destination database. This will
        wipe all data from the destination table.

        `Args:`
            source_table: str
                Full table path (e.g. ``my_schema.my_table``)
            destination_table: str
                Full table path (e.g. ``my_schema.my_table``)
            if_exists: str
                If destination table exists either ``drop``, ``truncate``, or ``drop_if_needed``.
                Truncate is useful when there are dependent views associated with the table.
                Drop if needed defaults to ``truncate``, but if an error occurs (because a data
                type or length has changed), it will instead ``drop``.
            order_by: str
                Name of the column to order rows by to ensure stable sorting of results across
                chunks.
            verify_row_count: bool
                Whether or not to verify the count of rows in the source and destination table
                are the same at the end of the sync.
            **kwargs: args
                Optional copy arguments for destination database.
        `Returns:`
            ``None``
        """

        # Create the table objects
        source_tbl = self.source_db.table(source_table)
        destination_tbl = self.dest_db.table(destination_table)

        logger.info(f"Syncing full table data from {source_table} to {destination_table}")

        # Drop or truncate if the destination table exists
        if destination_tbl.exists:
            if if_exists == "drop":
                destination_tbl.drop()
            elif if_exists == "truncate":
                self._check_column_match(source_tbl, destination_tbl)
                destination_tbl.truncate()
            elif if_exists == "drop_if_needed":
                try:
                    self._check_column_match(source_tbl, destination_tbl)
                    destination_tbl.truncate()
                except Exception:
                    logger.info(f"needed to drop {destination_tbl}...")
                    destination_tbl.drop()
            else:
                raise ValueError("Invalid if_exists argument. Must be drop or truncate.")

        # Create the table, if needed.
        if not destination_tbl.exists:
            self.create_table(source_table, destination_table)

        copied_rows = self.copy_rows(source_table, destination_table, None, order_by, **kwargs)

        if verify_row_count:
            self._row_count_verify(source_tbl, destination_tbl)

        logger.info(f"{source_table} synced: {copied_rows} total rows copied.")

    def table_sync_incremental(
        self,
        source_table: str,
        destination_table: str,
        primary_key: str,
        distinct_check: bool = True,
        verify_row_count: bool = True,
        strategy: Literal[
            "primary_key", "append_updates", "upsert_updates"
        ] = "primary_key",
        updated_at_column: str = "updated_at",
        **kwargs,
    ):
        """
        Incremental sync of table from a source database to a destination database
        using an incremental primary key or an update timestamp.

        `Args:`
            source_table: str
                Full table path (e.g. ``my_schema.my_table``)
            destination_table: str
                Full table path (e.g. ``my_schema.my_table``)
            primary_key: str
                The name of the primary key. This must be the same for the source and
                destination table.
            distinct_check: bool
                Check that the source table primary key is distinct prior to running the
                sync. If it is not, an error will be raised.
            verify_row_count: bool
                Whether or not to verify the count of rows in the source and destination table
                are the same at the end of the sync.
            strategy: Literal["primary_key", "append_updates", "upsert_updates"]
                Which strategy to use for incremental load.
                - primary_key: Loads all new rows with a primary key value larger than
                  those in the target table
                - append_updates: Uses a configurable updated_at column to find all rows
                  that have an updated_at value larger than the max in the target table, and
                  appends all those rows to the target table
                - upsert_updates: Uses a configurable updated_at column to find all rows
                  that have an updated_at value larger than the max in the target table, and
                  upserts all those rows to the target table
            **kwargs: args
                Optional copy arguments for destination database.
        `Returns:`
            ``None``
        """

        # Create the table objects
        source_tbl = self.source_db.table(source_table)
        destination_tbl = self.dest_db.table(destination_table)

        # Check that the destination table exists. If it does not, then run a
        # full sync instead.
        if not destination_tbl.exists:
            logger.info(
                "Destination tables %s does not exist, running a full sync",
                destination_table,
            )
            self.table_sync_full(source_table, destination_table, order_by=primary_key, **kwargs)
            return

        # Check that the source table primary key is distinct
        if distinct_check and not source_tbl.distinct_primary_key(primary_key):
            logger.info(
                "Checking for distinct values for column %s in table %s",
                primary_key,
                source_table,
            )
            raise ValueError("{primary_key} is not distinct in source table.")

        if strategy == "primary_key":
            # Get the max source table and destination table primary key
            logger.debug(
                "Calculating the maximum value for %s for source table %s",
                primary_key,
                source_table,
            )
            source_max = source_tbl.max_primary_key(primary_key)
            logger.debug(
                "Calculating the maximum value for %s for destination table %s",
                primary_key,
                destination_table,
            )
            dest_max = destination_tbl.max_primary_key(primary_key)
        else:
            # Get the max source table and destination table updated_at_column
            source_max = source_tbl.max_value(updated_at_column)
            dest_max = destination_tbl.max_value(updated_at_column)

        # Check for a mismatch in row counts; if dest_max_key is None, or destination is empty
        # and we don't have to worry about this check.
        if dest_max is not None and dest_max > source_max:
            raise ValueError("Destination DB key greater than source DB key.")

        # Do not copied if row counts are equal.
        elif dest_max == source_max:
            logger.info("Tables are already in sync.")
            return None

        elif strategy in ("primary_key", "append_updates"):
            rows_copied = self.copy_rows(
                source_table, destination_table, dest_max, primary_key, **kwargs
            )

            logger.info("Copied %s new rows to %s.", rows_copied, destination_table)

        elif strategy in ("primary_key", "upsert_updates"):
            rows_upserted = self.upsert_rows(
                source_table,
                destination_table,
                dest_max,
                updated_at_column,
                primary_key,
            )

            logger.info(
                "Upserted %s updated rows to %s.", rows_upserted, destination_table
            )

        if verify_row_count:
            if strategy == "append_updates":
                logger.warning("Cannot verify row counts when appending updated rows.")
            else:
                self._row_count_verify(source_tbl, destination_tbl)

        logger.info(f"{source_table} synced to {destination_table}.")

    def copy_rows(self, source_table_name, destination_table_name, cutoff, order_by, **kwargs):
        """
        Copy the rows from the source to the destination.

        `Args:`
            source_table_name: str
                Full table path (e.g. ``my_schema.my_table``)
            destination_table_name: str
                Full table path (e.g. ``my_schema.my_table``)
            cutoff:
                Start value to use as a minimum for incremental updates.
            order_by:
                Column to use to order the data to ensure a stable sort.
            **kwargs: args
                Optional copy arguments for destination database.
        `Returns:`
            ``None``
        """

        # Create the table objects
        source_table = self.source_db.table(source_table_name)

        # Initialize the Parsons table we will use to store rows before writing
        buffer = Table()

        # Track the number of retries we have left before giving up
        retries_left = self.retries + 1

        total_rows_downloaded = 0
        total_rows_written = 0
        rows_buffered = 0

        # Keep going until we break out
        while True:
            try:
                # Get the records to load into the database
                if cutoff:
                    # If we have a cutoff, we are loading data incrementally -- filter out
                    # any data before our cutoff
                    rows = source_table.get_new_rows(
                        primary_key=order_by,
                        cutoff_value=cutoff,
                        offset=total_rows_downloaded,
                        chunk_size=self.read_chunk_size,
                    )
                else:
                    # Get a chunk
                    rows = source_table.get_rows(
                        offset=total_rows_downloaded,
                        chunk_size=self.read_chunk_size,
                        order_by=order_by,
                    )

                number_of_rows = rows.num_rows
                total_rows_downloaded += number_of_rows

                # If we didn't get any data, exit the loop -- there's nothing to load
                if number_of_rows == 0:
                    # If we have any rows that are unwritten, flush them to the destination database
                    if rows_buffered > 0:
                        logger.debug(
                            "Copying %s rows to %s",
                            rows_buffered,
                            destination_table_name,
                        )
                        self.dest_db.copy(
                            buffer, destination_table_name, if_exists="append", **kwargs
                        )
                        total_rows_written += rows_buffered

                        # Reset the buffer
                        rows_buffered = 0
                        buffer = Table()

                    break

                # Add the new rows to our buffer
                buffer.concat(rows)
                rows_buffered += number_of_rows

                # If our buffer reaches our write threshold, write it out
                if rows_buffered >= self.write_chunk_size:
                    logger.debug("Copying %s rows to %s", rows_buffered, destination_table_name)
                    self.dest_db.copy(buffer, destination_table_name, if_exists="append", **kwargs)
                    total_rows_written += rows_buffered

                    # Reset the buffer
                    rows_buffered = 0
                    buffer = Table()

            except Exception:
                # Tick down the number of retries
                retries_left -= 1

                # If we are out of retries, fail
                if retries_left == 0:
                    logger.debug("No retries remaining")
                    raise

                # Otherwise, log the exception and try again
                logger.exception("Unhandled error copying data; retrying")

        return total_rows_written

    @staticmethod
    def _check_column_match(source_table_obj, destination_table_obj):
        """
        Ensure that the columns from each table match
        """

        if source_table_obj.columns != destination_table_obj.columns:
            raise ValueError(
                """Destination table columns do not match source table columns.
                             Consider dropping destination table and running a full sync."""
            )

    @staticmethod
    def _row_count_verify(source_table_obj, destination_table_obj):
        """
        Ensure the the rows of the source table and the destination table match
        """

        source_row_count = source_table_obj.num_rows
        dest_row_count = destination_table_obj.num_rows

        if source_row_count != dest_row_count:
            logger.warning(
                (
                    f"Table count mismatch. Source table contains {source_row_count}.",
                    f" Destination table contains {dest_row_count}.",
                )
            )
            return False

        logger.info("Source and destination table row counts match.")
        return True

    def create_table(self, source_table, destination_table):
        """
        Create the empty table in the destination database based on the source
        database schema structure. This method utilizes the Alchemy subclass.
        """

        # Try to create the destination using the source table's schema; if that doesn't work,
        # then we will lean on "copy" when loading the data to create the destination
        try:
            source_obj = self.source_db.get_table_object(source_table)
            self.dest_db.create_table(source_obj, destination_table)
        except Exception:
            logger.warning(
                "Unable to create destination table based on source table; we will "
                'fallback to using "copy" to create the destination.'
            )

    def upsert_rows(
        self,
        source_table_name: str,
        destination_table_name: str,
        cutoff: Union[
            str, int, float, datetime.date, datetime.datetime
        ],  # Type hint is probably incomplete
        updated_at_column: str,
        primary_key: str,
    ) -> int:
        """
        Upsert rows from the source to the destination based on updated_at_column

        `Args:`
            source_table_name: str
                Full table path (e.g. ``my_schema.my_table``)
            destination_table_name: str
                Full table path (e.g. ``my_schema.my_table``)
            cutoff:
                Start value to use as a minimum for updates.
            updated_at_column:
                Column which tracks the update timestamp
            primary_key:
                Column which serves as unique primary key
        `Returns:`
            total_rows_written: int
        """
        # Create the table objects
        source_table = self.source_db.table(source_table_name)

        # Initialize the Parsons table we will use to store rows before writing
        buffer = Table()

        total_rows_downloaded = 0
        total_rows_written = 0

        # Keep going until we break out
        while True:
            # Get the updated records to load into the database
            rows = source_table.get_updated_rows(
                updated_at_column=updated_at_column,
                cutoff_value=cutoff,
                offset=total_rows_downloaded,
                chunk_size=self.read_chunk_size,
            )

            number_of_rows = rows.num_rows
            total_rows_downloaded += number_of_rows

            # Add the new rows to our buffer
            buffer.concat(rows)

            # If our buffer reaches our write threshold, write it out
            if not len(rows) or len(buffer) >= self.write_chunk_size:
                logger.debug(
                    "Copying %s rows to %s", len(buffer), destination_table_name
                )
                if not self.dest_db.table_exists(destination_table_name):
                    self.dest_db.copy(
                        buffer, destination_table_name, if_exists="append"
                    )
                else:
                    # Load buffer to temp table, upsert from temp table
                    temp_table_name = (
                        destination_table_name
                        + "__stg_upsert_"
                        + datetime.datetime.today().strftime("%Y%m%d%H%M%S")
                    )
                    self.dest_db.copy(buffer, temp_table_name, if_exists="drop")
                    try:
                        self.dest_db.query(
                            f"""
                            delete from {destination_table_name}
                            where {primary_key} in (
                              select {primary_key} from {temp_table_name}
                            );
                            insert into {destination_table_name}
                            select * from {temp_table_name};
                            """
                        )
                    finally:
                        # Ensure this temp table gets dropped
                        self.dest_db.query(f"drop table {temp_table_name}")

                total_rows_written += len(buffer)

                # Reset the buffer
                buffer = Table()

            if not len(rows):
                break

        return total_rows_written
