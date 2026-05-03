import logging
from typing import Literal

from parsons import Table

logger = logging.getLogger(__name__)


class DBSync:
    """
    Sync tables between databases.

    Works with ``Postgres``, ``Redshift``, and ``MySQL`` databases.

    Args:
        source_db: Database connection object
        destination_db: Database connection object
        read_chunk_size:
            The number of rows to read from the source at a time when syncing a table.
            The default value is 100,000 rows.
        write_chunk_size:
            The number of rows to batch up before writing out to the destination.
            This value defaults to whatever the read_chunk_size is.
        retries:
            The number of times to retry if there is an error processing a chunk of data.
            The default value is 0.

    """

    def __init__(
        self,
        source_db: str,
        destination_db: str,
        read_chunk_size: int = 100_000,
        write_chunk_size=None,
        retries: int = 0,
    ) -> None:
        self.source_db = source_db
        self.dest_db = destination_db
        self.read_chunk_size = read_chunk_size
        self.write_chunk_size = write_chunk_size or read_chunk_size
        self.retries = retries

    def table_sync_full(
        self,
        source_table: str,
        destination_table: str,
        if_exists: Literal["drop", "truncate", "drop_if_needed"] = "drop",
        order_by: str | None = None,
        verify_row_count: bool = True,
        **kwargs,
    ) -> None:
        """
        Full sync of table from a source database to a destination database. This will
        wipe all data from the destination table.

        Args:
            source_table: Full table path (e.g. ``my_schema.my_table``)
            destination_table: Full table path (e.g. ``my_schema.my_table``)
            if_exists:
                If destination table exists either ``drop``, ``truncate``, or ``drop_if_needed``.
                Truncate is useful when there are dependent views associated with the table.
                Drop if needed defaults to ``truncate``, but if an error occurs (because a data
                type or length has changed), it will instead ``drop``.
            order_by:
                Name of the column to order rows by to ensure stable sorting of results across chunks.
            verify_row_count:
                Whether or not to verify the count of rows in the source and destination table
                are the same at the end of the sync.
            `**kwargs`: Optional copy arguments for destination database.

        Raises:
            ValueError: If ``if_exists`` is not a supported value.

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
        **kwargs,
    ) -> None:
        """
        Incremental sync of table from a source database to a
        destination database using an incremental primary key.

        Args:
            source_table: Full table path (e.g. ``my_schema.my_table``)
            destination_table: Full table path (e.g. ``my_schema.my_table``)
            primary_key:
                The name of the primary key.
                This must be the same for the source and destination table.
            distinct_check:
                Check that the source table primary key is distinct prior to running the sync.
                If it is not, an error will be raised.
            verify_row_count:
                Whether or not to verify the count of rows in the source and
                destination table are the same at the end of the sync.
            `**kwargs`: Optional copy arguments for destination database.

        Raises:
            ValueError:
                If the ``primary_key`` is not distinct in the ``source_table``.
                If the ``destination_table`` ``primary_key`` is greater than the ``source_table`` ``primary_key``.

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
            self.table_sync_full(
                source_table,
                destination_table,
                order_by=primary_key,
                verify_row_count=verify_row_count,
                **kwargs,
            )
            return None

        # Check that the source table primary key is distinct
        if distinct_check and not source_tbl.distinct_primary_key(primary_key):
            logger.info(
                "Checking for distinct values for column %s in table %s",
                primary_key,
                source_table,
            )
            raise ValueError("{primary_key} is not distinct in source table.")

        # Get the max source table and destination table primary key
        logger.debug(
            "Calculating the maximum value for %s for source table %s",
            primary_key,
            source_table,
        )
        source_max_pk = source_tbl.max_primary_key(primary_key)
        logger.debug(
            "Calculating the maximum value for %s for destination table %s",
            primary_key,
            destination_table,
        )
        dest_max_pk = destination_tbl.max_primary_key(primary_key)

        # Check for a mismatch in row counts; if dest_max_pk is None, or destination is empty
        # and we don't have to worry about this check.
        if dest_max_pk is not None and dest_max_pk > source_max_pk:
            raise ValueError("Destination DB primary key greater than source DB primary key.")

        # Do not copied if row counts are equal.
        elif dest_max_pk == source_max_pk:
            logger.info("Tables are already in sync.")
            return None

        else:
            rows_copied = self.copy_rows(
                source_table, destination_table, dest_max_pk, primary_key, **kwargs
            )
            logger.info("Copied %s new rows to %s.", rows_copied, destination_table)

        if verify_row_count:
            self._row_count_verify(source_tbl, destination_tbl)

        logger.info(f"{source_table} synced to {destination_table}.")

    def copy_rows(
        self, source_table_name: str, destination_table_name: str, cutoff, order_by: str, **kwargs
    ) -> int:
        """
        Copy the rows from the source to the destination.

        Args:
            source_table_name: Full table path (e.g. ``my_schema.my_table``)
            destination_table_name: Full table path (e.g. ``my_schema.my_table``)
            cutoff: Start value to use as a minimum for incremental updates.
            order_by: Column to use to order the data to ensure a stable sort.
            `**kwargs`: Optional copy arguments for destination database.

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
    def _check_column_match(source_table_obj, destination_table_obj) -> None:
        """Ensure that the columns from each table match"""
        if source_table_obj.columns != destination_table_obj.columns:
            raise ValueError(
                "Destination table columns do not match source table columns. "
                "Consider dropping destination table and running a full sync."
            )

    @staticmethod
    def _row_count_verify(source_table_obj, destination_table_obj) -> bool:
        """Ensure the the rows of the source table and the destination table match"""
        source_row_count = source_table_obj.num_rows
        dest_row_count = destination_table_obj.num_rows

        if source_row_count != dest_row_count:
            logger.warning(
                f"Table count mismatch. Source table contains {source_row_count}. "
                f"Destination table contains {dest_row_count}."
            )
            return False

        logger.info("Source and destination table row counts match.")
        return True

    def create_table(self, source_table: str, destination_table: str) -> None:
        """
        Create the empty table in the destination database based on the source database schema structure.

        This method utilizes the Alchemy subclass.
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
